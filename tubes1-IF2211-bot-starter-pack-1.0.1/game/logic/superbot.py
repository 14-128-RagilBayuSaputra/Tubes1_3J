import random
import math
from typing import Optional, List, Tuple, Dict, Any

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

MIN_DIAMONDS_TO_TACKLE = 5 
MAX_DISTANCE_TO_CONSIDER_TACKLE = 1 
TACKLE_SCORE_PENALTY = 10000.0 

SAFE_RETURN_BUFFER_SECONDS = 3
INVENTORY_SIZE_DEFAULT = 5
LOW_DIAMOND_THRESHOLD_FOR_RED_BUTTON = 4


class SuperBot(BaseLogic):
    def __init__(self):
        super().__init__()
        self.goal_position: Optional[Position] = None

    def _clamp(self, n, smallest, largest) -> int:
        return max(smallest, min(n, largest))

    def _position_equals(self, a: Position, b: Optional[Position]) -> bool:
        if b is None: return False
        return a.x == b.x and a.y == b.y

    def _get_manhattan_distance(self, pos1: Optional[Position], pos2: Optional[Position]) -> int:
        if pos1 is None or pos2 is None: return float('inf')
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def _get_teleporter_pair(self, teleport_obj: GameObject, all_teleporters: List[GameObject]) -> Optional[GameObject]:
        if len(all_teleporters) < 2: return None
        pair_id = getattr(teleport_obj.properties, 'pair_id', None)
        if pair_id is None:
            if len(all_teleporters) == 2:
                return next((t for t in all_teleporters if t.id != teleport_obj.id), None)
            return None
        return next((t for t in all_teleporters if t.id == pair_id), None)

    def _get_direction_advanced(self, current_pos: Position, dest_pos: Optional[Position],
                                avoid_positions_tuples: List[Tuple[int,int]],
                                board_width: int, board_height: int) -> Tuple[int, int]:
        if dest_pos is None: return 0,0
        current_x, current_y = current_pos.x, current_pos.y
        dest_x, dest_y = dest_pos.x, dest_pos.y
        delta_x_ideal = self._clamp(dest_x - current_x, -1, 1)
        delta_y_ideal = self._clamp(dest_y - current_y, -1, 1)
        if delta_x_ideal == 0 and delta_y_ideal == 0: return 0, 0
        
        preferred_moves = []
        if delta_x_ideal != 0: preferred_moves.append((delta_x_ideal, 0))
        if delta_y_ideal != 0: preferred_moves.append((0, delta_y_ideal))
        
        fallback_moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(fallback_moves)
        for move in fallback_moves:
            if move not in preferred_moves: preferred_moves.append(move)
            
        for dx, dy in preferred_moves:
            if dx != 0 and dy != 0: continue 
            next_x, next_y = current_x + dx, current_y + dy
            if 0 <= next_x < board_width and 0 <= next_y < board_height and \
               (next_x, next_y) not in avoid_positions_tuples:
                return dx, dy
        return 0, 0

    def _calculate_path(self, start_pos: Position, end_pos: Optional[Position], teleporters: List[GameObject]) \
            -> Tuple[int, Optional[GameObject], Optional[GameObject]]:
        if end_pos is None:
            return float('inf'), None, None
            
        dist_direct = self._get_manhattan_distance(start_pos, end_pos)
        dist_teleport = float('inf')
        best_tp_entry, best_tp_exit = None, None

        if len(teleporters) >= 2:
            for tp_e in teleporters:
                tp_x = self._get_teleporter_pair(tp_e, teleporters)
                if tp_e and hasattr(tp_e, 'position') and tp_e.position and \
                   tp_x and hasattr(tp_x, 'position') and tp_x.position:
                    d = self._get_manhattan_distance(start_pos, tp_e.position) + \
                        self._get_manhattan_distance(tp_x.position, end_pos)
                    if d < dist_teleport:
                        dist_teleport, best_tp_entry, best_tp_exit = d, tp_e, tp_x
        
        if dist_teleport < dist_direct:
            return dist_teleport, best_tp_entry, best_tp_exit
        return dist_direct, None, None

    def _evaluate_diamonds_by_distance_priority(self, current_pos: Position, diamonds: List[GameObject],
                                     teleporters: List[GameObject]) -> List[Dict[str, Any]]:
        diamond_targets = []
        for diamond in diamonds:
            diamond_points = getattr(diamond.properties, 'points', 0)
            if diamond_points == 0: continue

            dist_to_diamond, tp_entry_to_diamond, _ = self._calculate_path(current_pos, diamond.position, teleporters)
            if dist_to_diamond == float('inf'): continue
            
            score = -dist_to_diamond + (diamond_points * 0.01) 

            diamond_targets.append({
                "obj": diamond, "distance": dist_to_diamond, "points": diamond_points,
                "score_value": score, 
                "type": "diamond",
                "teleporter_entry": tp_entry_to_diamond
            })
        
        diamond_targets.sort(key=lambda x: x["score_value"], reverse=True)
        return diamond_targets

    def _evaluate_tackle_targets_deprioritized(self, board_bot: GameObject, other_bots: List[GameObject],
                                        teleporters: List[GameObject]) -> List[Dict[str, Any]]:
        my_props = board_bot.properties
        current_pos = board_bot.position
        inventory_size = getattr(my_props, 'inventory_size', INVENTORY_SIZE_DEFAULT)
        my_current_diamonds = getattr(my_props, 'diamonds', 0)
        tackle_targets = []

        for enemy_bot in other_bots:
            if not hasattr(enemy_bot, 'properties') or enemy_bot.properties is None: continue
            enemy_diamonds = getattr(enemy_bot.properties, 'diamonds', 0)

            if enemy_diamonds >= MIN_DIAMONDS_TO_TACKLE and my_current_diamonds < inventory_size:
                dist_to_enemy, tp_entry_to_enemy, _ = self._calculate_path(current_pos, enemy_bot.position, teleporters)
                if 0 < dist_to_enemy <= MAX_DISTANCE_TO_CONSIDER_TACKLE:
                    
                    tackle_score = (enemy_diamonds) - dist_to_enemy - TACKLE_SCORE_PENALTY 
                    tackle_targets.append({
                        "obj": enemy_bot, "distance": dist_to_enemy, "points": enemy_diamonds,
                        "score_value": tackle_score, "type": "tackle",
                        "teleporter_entry": tp_entry_to_enemy
                    })
        tackle_targets.sort(key=lambda x: x["score_value"], reverse=True)
        return tackle_targets

    def _should_return_to_base(self, board_bot: GameObject, board: Board, 
                                teleporters: List[GameObject],
                                best_next_item_overall: Optional[Dict[str,Any]]) -> Tuple[bool, Optional[Position], List[Tuple[int,int]]]:
        props = board_bot.properties
        current_pos = board_bot.position
        inventory_size = getattr(props, 'inventory_size', INVENTORY_SIZE_DEFAULT)
        my_current_diamonds = getattr(props, 'diamonds', 0)

        if my_current_diamonds == 0: 
            return False, None, []

        dist_to_base, tp_entry_for_base_obj, _ = self._calculate_path(current_pos, props.base, teleporters)
        time_left_seconds = props.milliseconds_left / 1000 if props.milliseconds_left is not None else float('inf')
        
        must_return = False
        if my_current_diamonds >= inventory_size: must_return = True
        elif (dist_to_base + SAFE_RETURN_BUFFER_SECONDS) >= time_left_seconds: must_return = True 
        elif my_current_diamonds == inventory_size - 1 and best_next_item_overall:
            if best_next_item_overall["type"] == "diamond" and best_next_item_overall["points"] == 2: must_return = True
        
        if not must_return: return False, None, []

        # Tentukan jalur dan hindaran untuk kembali ke base
        goal_for_base_return: Optional[Position] = props.base
        avoid_for_base_return_tuples: List[Tuple[int,int]] = [] 
        other_bots_on_board = [bot for bot in board.bots if bot.id != board_bot.id]
        for ob in other_bots_on_board: avoid_for_base_return_tuples.append((ob.position.x, ob.position.y))

        if tp_entry_for_base_obj and tp_entry_for_base_obj.position:
             # Hitung ulang jarak efektif via teleporter untuk kepastian
            tp_exit_for_base = self._get_teleporter_pair(tp_entry_for_base_obj, teleporters)
            if tp_exit_for_base and tp_exit_for_base.position:
                path_to_base_via_tp_dist = self._get_manhattan_distance(current_pos, tp_entry_for_base_obj.position) + \
                                           self._get_manhattan_distance(tp_exit_for_base.position, props.base)
                if path_to_base_via_tp_dist < dist_to_base: 
                    if not self._position_equals(current_pos, tp_entry_for_base_obj.position):
                        goal_for_base_return = tp_entry_for_base_obj.position
        
        # Atur hindaran teleporter
        if goal_for_base_return == (tp_entry_for_base_obj.position if tp_entry_for_base_obj else None) : 
            for t in teleporters:
                if not self._position_equals(t.position, goal_for_base_return):
                    avoid_for_base_return_tuples.append((t.position.x, t.position.y))
        else: 
            for t in teleporters:
                avoid_for_base_return_tuples.append((t.position.x, t.position.y))
        
        if goal_for_base_return and goal_for_base_return != props.base: 
            if (goal_for_base_return.x, goal_for_base_return.y) in avoid_for_base_return_tuples:
                avoid_for_base_return_tuples.remove((goal_for_base_return.x, goal_for_base_return.y))
                
        return True, goal_for_base_return, avoid_for_base_return_tuples

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        props = board_bot.properties
        current_pos = board_bot.position

        red_buttons = [obj for obj in board.game_objects if obj.type == "DiamondButtonGameObject"]
        teleporters = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]
        diamonds = board.diamonds
        other_bots = [bot for bot in board.bots if bot.id != board_bot.id]
        
        diamond_targets = self._evaluate_diamonds_by_distance_priority(current_pos, diamonds, teleporters)
        tackle_targets = self._evaluate_tackle_targets_deprioritized(board_bot, other_bots, teleporters)

        all_targets = diamond_targets + tackle_targets
        all_targets.sort(key=lambda x: x["score_value"], reverse=True) 
        
        best_overall_target: Optional[Dict[str, Any]] = None
        if all_targets:
            best_overall_target = all_targets[0]

        must_return, base_goal_pos, base_avoid_tuples = \
            self._should_return_to_base(board_bot, board, teleporters, best_overall_target)

        if must_return and base_goal_pos is not None:
            self.goal_position = base_goal_pos
            return self._get_direction_advanced(current_pos, self.goal_position, base_avoid_tuples, board.width, board.height)

        current_action_avoid_tuples = [(b.position.x, b.position.y) for b in other_bots] 

        if best_overall_target and best_overall_target["score_value"] > - (board.width + board.height) * 2 : 
            target_object = best_overall_target["obj"]
            self.goal_position = target_object.position 
            
            tp_entry_for_target_obj = best_overall_target.get("teleporter_entry") 
            if tp_entry_for_target_obj and tp_entry_for_target_obj.position and \
               not self._position_equals(current_pos, tp_entry_for_target_obj.position):
                self.goal_position = tp_entry_for_target_obj.position 

            if best_overall_target["type"] == "tackle":
                current_action_avoid_tuples = [(b.position.x, b.position.y) for b in other_bots if b.id != target_object.id]
                for t in teleporters: current_action_avoid_tuples.append((t.position.x,t.position.y))
            else: 
                for t in teleporters: 
                    if not self._position_equals(t.position, self.goal_position): 
                        current_action_avoid_tuples.append((t.position.x,t.position.y))
            
                if tp_entry_for_target_obj and self.goal_position and self._position_equals(self.goal_position, tp_entry_for_target_obj.position):
                    if (self.goal_position.x, self.goal_position.y) in current_action_avoid_tuples:
                        current_action_avoid_tuples.remove((self.goal_position.x, self.goal_position.y))
            
            if self.goal_position: 
                 return self._get_direction_advanced(current_pos, self.goal_position, current_action_avoid_tuples, board.width, board.height)

        if red_buttons and (not diamonds or len(diamonds) < LOW_DIAMOND_THRESHOLD_FOR_RED_BUTTON):
            self.goal_position = red_buttons[0].position
            avoid_for_red = [(b.position.x, b.position.y) for b in other_bots]
            for t in teleporters: avoid_for_red.append((t.position.x,t.position.y))
            if self.goal_position:
                return self._get_direction_advanced(current_pos, self.goal_position, avoid_for_red, board.width, board.height)
        
        return 0,0 