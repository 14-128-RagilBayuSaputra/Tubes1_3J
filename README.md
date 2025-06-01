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
```
---
## iii. Cara Menjalankan Bot

1. Clone repository terkait:
```bash
git clone https://github.com/haziqam/tubes1-IF2211-game-engine.git
git clone https://github.com/haziqam/tubes1-IF2211-bot-starter-pack.git
```

2. Salin file SuperBot.py ke folder logic di starter pack.

3. Jalankan game engine:
```bash
cd tubes1-IF2211-game-engine
npm install
npm start
```

4. Jalankan bot:
```bash
cd tubes1-IF2211-bot-starter-pack
python main.py
```

5. Konfigurasi
Edit main.py untuk menyesuaikan email, nama bot, password, dan boardId sesuai yang digunakan.

---
## iv. Author
Kelompok 8 - IF2211 Kelas RD
Tugas Besar Strategi Algoritma - Institut Teknologi Sumatera (ITERA)
- Cikal Galih Nur Arifin (123140109)
- Ragil Bayu Saputra (123140128)
- Rafael Abimanyu Ratmoko (123140134)
