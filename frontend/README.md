# Edusight — Frontend Client

Frontend SPA (Single Page Application) React.js untuk platform **Edusight**. Antarmuka ini menampilkan dashboard pembelajaran adaptif, kurikulum materi sekuensial, kuis interaktif, serta visualisasi ulasan AI kognitif.

## Tech Stack

*   **Framework**: React.js (Vite)
*   **CSS**: Tailwind CSS
*   **Charts/Visuals**: Recharts (Radar Chart & Doughnut Chart)
*   **Icons**: Lucide React
*   **API Client**: Axios

## Setup & Menjalankan Lokal

Pastikan Node.js (versi 18+) telah terpasang di komputer Anda.

```bash
# 1. Masuk ke folder frontend
cd frontend

# 2. Pasang dependensi Node.js
npm install

# 3. Jalankan server development
npm run dev
```

Aplikasi web dapat diakses secara lokal di `http://localhost:5173`.

## Konfigurasi Env (.env)
Untuk menghubungkan dengan backend, buat file `.env` di folder `frontend/` jika dibutuhkan:
```text
VITE_API_URL=http://localhost:8000
```

## Build Produksi
Untuk melakukan kompilasi bundel production:
```bash
npm run build
```
Hasil build akan tersimpan di dalam folder `dist/` dan siap dideploy ke Vercel/Netlify.
