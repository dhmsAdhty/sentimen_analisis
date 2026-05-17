# 📘 Dokumentasi Proyek SentimenAI
### Panduan untuk Pemula — Memahami Backend & Frontend

---

## 🤔 Apa itu Backend dan Frontend?

Bayangkan sebuah **restoran** 🍽️

| Bagian Restoran | Di Dunia Web |
|---|---|
| **Dapur** (tempat masak, tidak kelihatan tamu) | **Backend** — tempat data diolah |
| **Ruang makan** (yang dilihat & digunakan tamu) | **Frontend** — tampilan yang dilihat pengguna |
| **Pelayan** (pengantar pesanan dapur → tamu) | **API** — penghubung backend & frontend |

Jadi dalam proyek ini:
- **Frontend** = tampilan web yang kamu buka di browser (Vue.js)
- **Backend** = program Python yang mengolah data di balik layar (FastAPI)
- **API** = "jembatan" yang menghubungkan keduanya

---

## 🗂️ Struktur Folder Proyek

```
Cluster_Sentimen_app/
│
├── 📁 backend/              ← DAPUR (Python / FastAPI)
│   ├── main.py              ← File utama backend (semua "resep" ada di sini)
│   ├── models/              ← File model AI yang sudah dilatih (.pkl)
│   │   ├── rf_model.pkl
│   │   ├── tfidf_sentiment.pkl
│   │   ├── kmeans_model.pkl
│   │   └── tfidf_cluster.pkl
│   ├── temp_data/           ← Penyimpanan sementara data pengguna
│   └── utils/               ← Fungsi-fungsi pembantu
│       ├── preprocessing.py ← Proses teks (tokenisasi, stemming, dll)
│       ├── lexicon.py       ← Kamus sentimen (positif/negatif)
│       ├── predictor.py     ← Fungsi prediksi sentimen & cluster
│       └── scraper.py       ← Ambil data dari Google Maps
│
└── 📁 frontend/             ← RUANG MAKAN (Vue.js / Vite)
    └── src/
        ├── views/           ← Halaman-halaman website
        │   ├── Beranda.vue
        │   ├── DataInput.vue
        │   ├── Preprocessing.vue
        │   ├── Clustering.vue
        │   ├── TopikCluster.vue
        │   ├── Labeling.vue
        │   ├── Training.vue
        │   ├── Evaluasi.vue
        │   ├── Insight.vue
        │   └── KlasifikasiBaru.vue
        ├── components/      ← Bagian kecil yang bisa dipakai ulang
        │   ├── Navbar.vue   ← Menu navigasi atas
        │   ├── PipelineNav.vue ← Tombol next/prev antar halaman
        │   └── ShapeGrid.vue   ← Animasi kotak-kotak di background
        ├── router/
        │   └── index.js     ← Daftar URL halaman website
        └── store/
            └── index.js     ← Penyimpanan data sementara di browser
```

---

## ▶️ Cara Menjalankan Proyek (Step by Step)

> **Penting:** Kamu butuh 2 terminal terbuka sekaligus!

### Terminal 1 — Jalankan Backend (Dapur)

```bash
# Masuk ke folder backend
cd Cluster_Sentimen_app/backend

# Jalankan server Python
uvicorn main:app --reload --port 8000
```

Kalau berhasil, akan muncul:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Artinya:** Dapur sudah buka! Backend siap menerima pesanan.

---

### Terminal 2 — Jalankan Frontend (Ruang Makan)

```bash
# Masuk ke folder frontend
cd Cluster_Sentimen_app/frontend

# Jalankan website
npm run dev
```

Kalau berhasil, akan muncul:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

**Artinya:** Ruang makan sudah buka! Buka browser dan akses `http://localhost:5173`

---

## 🔄 Bagaimana Backend dan Frontend Berkomunikasi?

Analoginya seperti tamu memesan makanan:

```
[Browser / Frontend]          [Backend / Python]
       |                              |
       | 1. Klik tombol "Upload"      |
       |----------------------------->|
       |   Kirim file CSV             |
       |                              | 2. Python baca file,
       |                              |    simpan sementara
       |                              |    (temp_data/)
       | 3. Terima balasan:           |
       |    "Upload berhasil!         |<-------------|
       |     200 data ditemukan"      |
       |                              |
```

Komunikasi ini dilakukan lewat **HTTP Request** ke URL tertentu.

---

## 🗺️ Daftar API Endpoint (Semua "Pintu" ke Backend)

| Endpoint URL | Fungsi | Dipakai di halaman |
|---|---|---|
| `POST /api/data/upload` | Upload file CSV/Excel | Input Data |
| `POST /api/data/scrape` | Ambil review Google Maps | Input Data |
| `POST /api/data/clean` | Hapus data duplikat & kosong | Input Data |
| `POST /api/process/preprocess` | Bersihkan teks (NLP) | Preprocessing |
| `POST /api/cluster/evaluate` | Hitung nilai K terbaik | Clustering |
| `POST /api/cluster/apply` | Terapkan K-Means clustering | Clustering |
| `POST /api/cluster/topic` | Ambil kata kunci per cluster | Topik Cluster |
| `POST /api/sentiment/label` | Beri label sentimen (Lexicon) | Labeling |
| `POST /api/data/info` | Info statistik dataset | Training |
| `POST /api/model/train` | Latih model Random Forest | Training |
| `POST /api/insight` | Ringkasan global data | Insight |
| `POST /api/model/predict` | Prediksi 1 teks baru | Klasifikasi Baru |
| `POST /api/model/predict_batch` | Prediksi banyak data (file) | Klasifikasi Baru |

---

## 🔢 Urutan Penggunaan Aplikasi (Pipeline 9 Langkah)

```
LANGKAH 1: Input Data
  → Upload file CSV/Excel yang berisi kolom "Review"
  → Atau scraping dari Google Maps
  → Lakukan Cleaning (hapus duplikat & data kosong)
        ↓
LANGKAH 2: Preprocessing
  → Teks dibersihkan secara otomatis:
    - Huruf besar → kecil semua
    - Hapus tanda baca & angka
    - Hapus kata tidak penting (stopword): "yang", "dan", "di"
    - Ubah ke kata dasar (stemming): "berlari" → "lari"
        ↓
LANGKAH 3: Clustering K-Means
  → Sistem mencari "K" (jumlah kelompok) terbaik
  → Evaluasi dengan 3 metrik: Elbow, Silhouette, Calinski-Harabasz
  → Tekan "Lakukan Clustering" untuk menerapkan
        ↓
LANGKAH 4: Topik Cluster
  → Lihat kata-kata paling dominan di setiap kelompok
  → Menggunakan TF-IDF (ukuran kepentingan kata)
        ↓
LANGKAH 5: Labeling Sentimen
  → Setiap ulasan diberi label otomatis:
    - 2 = Positif 😊
    - 1 = Netral 😐
    - 0 = Negatif 😞
  → Menggunakan kamus Lexicon Bahasa Indonesia
        ↓
LANGKAH 6: Training Model
  → Model Random Forest dilatih dengan data berlabel
  → Atur berapa fitur TF-IDF dan ukuran data test
        ↓
LANGKAH 7: Evaluasi Model
  → Lihat seberapa akurat model:
    - Classification Report (presisi, recall, F1)
    - Confusion Matrix (visualisasi kesalahan prediksi)
        ↓
LANGKAH 8: Insight
  → Ringkasan otomatis seluruh analisis
  → Distribusi sentimen & cluster dalam grafik
        ↓
LANGKAH 9: Klasifikasi Baru
  → Masukkan teks baru → langsung tahu sentimennya
  → Atau upload file baru untuk prediksi massal
```

---

## 🧰 Teknologi yang Digunakan

### Backend (Python)
| Library | Fungsi |
|---|---|
| **FastAPI** | Framework web untuk membuat API Python |
| **Uvicorn** | Server untuk menjalankan FastAPI |
| **Pandas** | Baca dan olah data CSV/Excel |
| **Scikit-learn** | Machine learning (K-Means, Random Forest, TF-IDF) |
| **PySastrawi** | Stemming Bahasa Indonesia |
| **Joblib** | Simpan & muat model ML (.pkl) |

### Frontend (JavaScript/Vue)
| Library | Fungsi |
|---|---|
| **Vue.js 3** | Framework untuk membangun tampilan web |
| **Vite** | Alat untuk menjalankan & build proyek Vue |
| **Vue Router** | Mengatur navigasi antar halaman |
| **Pinia** | Penyimpanan data sementara di browser |
| **Axios** | Kirim request ke backend (seperti "pelayan") |
| **Chart.js** | Membuat grafik interaktif |
| **Tailwind CSS** | Styling tampilan web |

---

## 💾 Penyimpanan Data

### Di Backend (Sementara)
Data tersimpan di folder `temp_data/` dengan format:
```
{session_id}_raw.csv          ← Data mentah setelah upload
{session_id}_clean.csv        ← Setelah cleaning
{session_id}_preprocessed.csv ← Setelah preprocessing NLP
{session_id}_clustered.csv    ← Setelah clustering
{session_id}_labeled.csv      ← Setelah labeling sentimen
```

**`session_id`** adalah kode unik (seperti nomor meja di restoran) yang diberikan saat pertama kali upload data. Kode ini dipakai di setiap langkah berikutnya.

### Di Frontend (Browser)
Disimpan di **LocalStorage** browser:
- `session_id` → agar tidak hilang saat halaman di-refresh
- Hasil training (akurasi, confusion matrix) → agar Evaluasi tetap tampil

---

## ❓ FAQ (Pertanyaan Umum)

**Q: Kenapa harus jalankan 2 terminal?**  
A: Karena backend (Python) dan frontend (Vue) adalah 2 program berbeda yang berjalan di port berbeda. Backend di port `8000`, frontend di port `5173`.

---

**Q: Apa yang terjadi kalau backend tidak jalan?**  
A: Frontend akan tetap tampil, tapi semua tombol yang butuh data (upload, preprocessing, dll) tidak akan berfungsi. Halaman Beranda akan menampilkan pesan "Backend tidak terdeteksi".

---

**Q: Kenapa pakai session_id?**  
A: Karena bisa ada banyak pengguna sekaligus. Setiap pengguna punya "kode meja" sendiri sehingga data mereka tidak bercampur.

---

**Q: Di mana model AI disimpan?**  
A: Di folder `backend/models/`. Ada 4 file:
- `rf_model.pkl` → Model Random Forest untuk prediksi sentimen
- `tfidf_sentiment.pkl` → Vectorizer TF-IDF untuk sentimen
- `kmeans_model.pkl` → Model K-Means untuk clustering
- `tfidf_cluster.pkl` → Vectorizer TF-IDF untuk clustering

---

**Q: Apakah data saya aman?**  
A: Data hanya tersimpan sementara di folder `temp_data/` di komputer lokal. Tidak dikirim ke server lain karena ini aplikasi lokal.

---

**Q: Format file apa yang didukung untuk upload?**  
A: `.csv` dan `.xlsx` (Excel). File **wajib memiliki kolom bernama `Review`** (dengan huruf R kapital).

---

**Q: Apa bedanya Lexicon dan Random Forest?**  
A: 
- **Lexicon** (Langkah 5) = pelabelan berdasarkan kamus kata positif/negatif. Cepat tapi sederhana.
- **Random Forest** (Langkah 6-7) = model Machine Learning yang belajar dari data. Lebih akurat untuk data baru.

---

## 🚀 Cara Install dari Awal (Fresh Install)

### Syarat:
- Python 3.9 atau lebih baru
- Node.js 18 atau lebih baru

### Backend:
```bash
cd Cluster_Sentimen_app/backend
pip install fastapi uvicorn pandas scikit-learn joblib PySastrawi
uvicorn main:app --reload --port 8000
```

### Frontend:
```bash
cd Cluster_Sentimen_app/frontend
npm install
npm run dev
```

Buka browser → `http://localhost:5173`

---

*Dokumentasi ini dibuat untuk memudahkan pemahaman tentang arsitektur decoupled (terpisah) antara Backend dan Frontend pada proyek Analisis Sentimen.*
