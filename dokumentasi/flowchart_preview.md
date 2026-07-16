# Perbaikan Flowchart Aplikasi Edusight

Berikut adalah kode rancangan **Mermaid Diagram** untuk flowchart Edusight yang sudah diperbaiki. 

Rancangan ini **mempertahankan seluruh kotak asli** dari gambar `flowchart_aplikasi.png` Anda dan hanya mengubah jalur hubungannya (koneksi) serta menyisipkan log login di bagian atas agar logikanya 100% benar untuk skripsi.

---

## 📊 Kode Flowchart Hasil Perbaikan (Mermaid)

```mermaid
graph TD
    %% Node Styling (Warna biru untuk proses, merah muda untuk DB)
    classDef process fill:#b3d9ff,stroke:#333,stroke-width:1px;
    classDef database fill:#ffb3b3,stroke:#333,stroke-width:1px;

    %% Alur Atas (Pencatatan Login)
    Start([Mulai]) --> Login[Input Username & Password]
    Login --> DB_Login[(Simpan Log Login ke user_activities)]
    DB_Login --> Dashboard[Tampilkan Dashboard Utama]

    %% Pilihan Menu Navigasi
    Dashboard --> NavMenu{Pilih Menu}
    
    %% Alur AI Insight (Tetap seperti aslinya)
    NavMenu -->|AI Insight| AI_Page[Tampilkan AI Recommendation & Klaster Gaya Belajar]
    AI_Page --> Dashboard
    
    %% Alur Jalur Belajar & Kuis (Digabungkan berurutan dari atas ke bawah)
    NavMenu -->|Materi Belajar| ReadModul[Membaca Materi / Jalur Belajar]
    ReadModul --> StartTime[Catat Waktu Mulai & Selesai Belajar]
    StartTime --> MarkRead[Klik Selesai & Tandai Dibaca]
    
    %% Cabang Database dan Alur Kuis
    MarkRead --> DB_Activity[(Simpan ke completion_log & learning_activities)]
    MarkRead --> StartQuiz[Kerjakan Kuis Pilihan Ganda]
    
    %% Penyelesaian Kuis
    StartQuiz --> SubmitQuiz[Kirim Jawaban Kuis]
    SubmitQuiz --> DB_Quiz[(Simpan Skor & Percobaan ke quiz_attempts)]
    
    %% Pembukaan Kunci Bab & Kembali ke Halaman Materi
    DB_Quiz --> UnlockNext[Buka Kunci Materi Berikutnya]
    UnlockNext --> ReadModul

    %% Style
    class Login,Dashboard,AI_Page,ReadModul,StartTime,MarkRead,StartQuiz,SubmitQuiz,UnlockNext process;
    class DB_Login,DB_Activity,DB_Quiz database;
```

---

## 🔧 Ringkasan Perubahan dari Flowchart Asli Anda:

1.  **Ditambahkan di Awal:** Kotak database **`Simpan Log Login ke user_activities`** ditambahkan tepat sebelum masuk ke *Tampilkan Dashboard Utama*.
2.  **Digabungkan secara Berurutan:** Kotak **`Kerjakan Kuis Pilihan Ganda`** yang tadinya berdiri sejajar di kolom kanan, kini diletakkan di bawah kotak **`Klik Selesai & Tandai Dibaca`** karena kuis hanya bisa diakses setelah materi bab selesai dibaca.
3.  **Panah Kembali ke Materi:** Kotak **`Buka Kunci Materi Berikutnya`** di bagian akhir kini memiliki panah kembali ke **`Membaca Materi / Jalur Belajar`** (bukan ke Dashboard utama) agar siswa bisa langsung memilih bab berikutnya yang baru terbuka.
