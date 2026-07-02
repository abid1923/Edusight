# Edusight — Platform Pembelajaran Adaptif Cerdas Berbasis AI

Edusight adalah platform pembelajaran adaptif berbasis kecerdasan buatan (AI) yang mengklasifikasikan gaya belajar pengguna menggunakan algoritma **K-Means Clustering** dan menyajikan ulasan kognitif personal menggunakan **LLM Llama 3.3** via Groq Cloud API, serta memberikan rekomendasi materi terarah secara dinamis.

---

## 🚀 Tumpukan Teknologi (Tech Stack)

*   **Frontend:** React.js (Vite), Tailwind CSS, Recharts (Radar & Doughnut Chart), Lucide React.
*   **Backend:** FastAPI (Python), SQLAlchemy ORM, Uvicorn, SQLite (Lokal) & PostgreSQL/Supabase (Production).
*   **Kecerdasan Buatan:** Scikit-learn (K-Means & MinMaxScaler), Groq SDK (Llama 3.3-70b-versatile).

---

## 📁 Struktur Repositori

Proyek ini terbagi menjadi dua komponen utama:
*   **`backend/`**: Direktori API backend FastAPI, modul komputasi Machine Learning, dan integrasi LLM.
*   **`frontend/`**: Direktori antarmuka pengguna berbasis React.js (Vite) untuk visualisasi dashboard belajar.

---

## 🛠️ Cara Menjalankan Aplikasi Secara Lokal

### 1. Menjalankan Backend FastAPI
Masuk ke folder backend, aktifkan virtual environment, pasang dependensi, dan jalankan server development:
```bash
cd backend
# Aktifkan virtual environment di Windows
..\.venv\Scripts\activate
# Jalankan server
uvicorn app.main:app --reload
```
Dokumentasi API Swagger otomatis aktif di `http://localhost:8000/docs`.

### 2. Menjalankan Frontend React
Buka terminal baru, masuk ke folder frontend, pasang dependensi Node, dan jalankan server development:
```bash
cd frontend
npm install
npm run dev
```
Aplikasi web dapat diakses secara lokal di `http://localhost:5173`.
