# Tubes1_3J

## i. Penjelasan Singkat Algoritma Greedy

Bot ini dirancang untuk berkompetisi dalam permainan *Diamonds*, sebuah game pengumpulan poin di mana bot harus mengumpulkan sebanyak mungkin diamond di papan permainan. Strategi utama yang digunakan adalah kombinasi dari beberapa pendekatan **algoritma greedy**, yaitu:

1. **Greedy by Distance** – Memilih diamond dengan jarak terpendek dari posisi bot.
2. **Greedy by Points** – Memprioritaskan diamond merah (2 poin) dibandingkan biru (1 poin).
3. **Greedy by Tackle** – Mengejar dan mentackle bot lawan yang membawa banyak diamond untuk mencuri poin mereka.

Bot akan mengevaluasi semua kemungkinan aksi di tiap tick berdasarkan skor heuristik yang dihitung dari kombinasi nilai dan jarak. Bot juga mempertimbangkan penggunaan **teleporter**, **red button**, dan risiko **tackle** oleh bot lawan.

---

## ii. Requirement Program dan Instalasi

Untuk menjalankan program ini, pastikan environment Python lo sudah siap dengan beberapa dependencies berikut:

- Python 3.8 atau lebih tinggi
- `requests`
- `typing` (jika pakai Python <3.9)
- Game Engine dari repo ini:  
  [Game Engine Link](https://github.com/haziqam/tubes1-IF2211-game-engine/releases/tag/v1.1.0)
- Bot Starter Pack dari repo ini:  
  [Bot Starter Pack Link](https://github.com/haziqam/tubes1-IF2211-bot-starter-pack/releases/tag/v1.0.1)

Instalasi dependencies bisa dilakukan lewat:

```bash
pip install -r requirements.txt
