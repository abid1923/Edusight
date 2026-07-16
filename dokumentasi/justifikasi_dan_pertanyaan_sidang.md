# 🎓 Panduan Justifikasi Desain Sistem & Kisi-Kisi Sidang Skripsi Edusight

Dokumen ini merangkum seluruh diskusi kritis mengenai justifikasi desain sistem, arsitektur database, algoritma Machine Learning K-Means, dan sistem rekomendasi AI di Edusight. 

Dokumen ini disusun dalam format **Tanya-Jawab Akademis** untuk membantu Anda menulis **Bab 4 (Pembahasan)**, **Bab 5 (Kesimpulan & Saran)**, serta sebagai persiapan mental menghadapi **Sidang Pertanggungjawaban Skripsi**.

---

## 📂 DAFTAR ISI JUSTIFIKASI:

### Bagian A: Alur Belajar & Model AI Adaptif
1. [Justifikasi 1: Pemisahan Tabel `learning_activities` dan `completion_logs`](#1-justifikasi-pemisahan-tabel-learning_activities-dan-completion_logs)
2. [Justifikasi 2: Rekomendasi AI pada Bab yang Masih Terkunci](#2-justifikasi-rekomendasi-ai-pada-bab-yang-masih-terkunci)
3. [Justifikasi 3: Rute Navigasi Rekomendasi AI ke Halaman Utama Jalur Belajar (UX Limitation)](#3-rute-navigasi-rekomendasi-ai-ke-halaman-utama-jalur-belajar-ux-limitation)
4. [Justifikasi 4: Desain Pembukaan Bab secara Sekuensial (Penguncian Bab)](#4-desain-pembukaan-bab-secara-sekuensial-penguncian-bab)
5. [Justifikasi 5: Deteksi Perilaku "Gaming the System" (Klik Cepat & Gagal Kuis)](#5-deteksi-perilaku-gaming-the-system-klik-cepat-gagal-kuis)

### Bagian B: Keamanan, Deployment, Rekayasa Data, & Infrastruktur
6. [Justifikasi 6: Keamanan File Baru di Folder Terhubung Git/GitHub](#6-justifikasi-keamanan-file-baru-di-folder-terhubung-gitgithub)
7. [Justifikasi 7: Ketiadaan UI Admin Panel Khusus](#7-justifikasi-ketiadaan-ui-admin-panel-khusus)
8. [Justifikasi 8: Penambahan Data Pengguna Simulasi (Rekayasa Data Skripsi)](#8-justifikasi-penambahan-data-pengguna-simulasi-rekayasa-data-skripsi)
9. [Justifikasi 9: Kemudahan Melakukan Revisi Pasca-Deployment](#9-justifikasi-kemudahan-melakukan-revisi-pasca-deployment)
10. [Justifikasi 10: Batas Akses Pengguna Bersamaan (Concurrent Users Limit)](#10-justifikasi-batas-akses-pengguna-bersamaan-concurrent-users-limit)
11. [Justifikasi 11: Jumlah Tabel Database yang Banyak (Normalisasi 3NF)](#11-justifikasi-jumlah-tabel-database-yang-banyak-normalisasi-3nf)

---

### 1. Justifikasi Pemisahan Tabel `learning_activities` dan `completion_logs`

*   **Pertanyaan Penguji:**
    *"Mengapa Anda memisahkan tabel `learning_activities` dengan `completion_logs`? Bukankah kedua tabel tersebut sama-sama mencatat bahwa siswa telah menyelesaikan membaca materi?"*
*   **Jawaban Akademis Anda:**
    > *"Pemisahan kedua tabel ini didasarkan pada prinsip **Normalisasi Database** dan **Analisis Deret Waktu (Time-series Analysis)**. 
    > 
    > Tabel **`learning_activities`** bersifat **multi-record (berulang)**. Setiap kali siswa membaca Bab 1 (misal membaca ulang sebanyak 3 kali), sistem akan mencatat 3 baris data baru dengan durasi membaca yang berbeda-beda. Data ini penting sebagai fitur input kognitif untuk K-Means.
    > 
    > Sedangkan tabel **`completion_logs`** bersifat **single-record (unik)**. Tabel ini hanya mencatat status akhir biner (Tuntas/Tidak) per bab untuk kebutuhan kontrol akses (*LMS Sequencing*) agar sistem tahu kapan harus membuka kunci Bab berikutnya."*

---

### 2. Justifikasi Rekomendasi AI pada Bab yang Masih Terkunci

*   **Pertanyaan Penguji:**
    *"Mengapa sistem rekomendasi AI (Groq/LLM) tetap merekomendasikan Bab 5 kepada siswa, padahal bab tersebut saat ini masih terkunci karena siswa baru menyelesaikan Bab 2?"*
*   **Jawaban Akademis Anda:**
    > *"Rekomendasi AI pada Edusight menerapkan metode **Goal-Directed Recommendation (Rekomendasi Berbasis Target Pencapaian)**. 
    > 
    > AI tidak hanya merekomendasikan apa yang bisa diakses secara instan, melainkan memproyeksikan **target kompetensi jangka pendek/menengah** yang paling sesuai dengan gaya belajar siswa. 
    > 
    > Hal ini didukung oleh teori psikologi pendidikan untuk memicu **motivasi belajar intrinsik**. Rekomendasi bab yang terkunci bertindak sebagai sasaran/tujuan kompetensi yang merangsang siswa untuk segera menuntaskan bab-bab prasyarat di bawahnya."*

---

### 3. Rute Navigasi Rekomendasi AI ke Halaman Utama Jalur Belajar (UX Limitation)

*   **Pertanyaan Penguji:**
    *"Mengapa tombol 'Mulai Belajar' pada rekomendasi materi internal mengarahkan pengguna ke halaman pilihan Jalur Belajar terlebih dahulu, bukan langsung membuka slide bab yang direkomendasikan?"*
*   **Jawaban Akademis Anda:**
    > *"Ini merupakan kombinasi dari **aspek stabilitas program (State Safety)** dan **keterbatasan integrasi data (Data Type Limitation)**:
    > 
    > 1. **Keterbatasan Data:** Data rekomendasi AI yang disimpan di database berfokus pada nama teks topik (`path_name`), bukan ID numerik materi. Oleh karena itu, frontend mengarahkan ke halaman Jalur Belajar sesuai nama topik tersebut.
    > 2. **Keamanan State Aplikasi:** Halaman slide materi membutuhkan inisialisasi data jalur belajar yang memadai di memori React. Jika dipaksa melompat langsung ke bab tertentu dari luar (terutama jika bab tersebut masih berstatus terkunci), aplikasi berisiko mengalami error/crash. Mengarahkan siswa ke gerbang Jalur Belajar adalah langkah teraman yang memvalidasi hak akses siswa secara prosedural."*

---

### 4. Desain Pembukaan Bab secara Sekuensial (Penguncian Bab)

*   **Pertanyaan Penguji:**
    *"Mengapa Anda menerapkan sistem penguncian bab secara sekuensial (harus menyelesaikan bab $N$ untuk membuka bab $N+1$)? Apakah ini tidak membatasi kebebasan belajar siswa di platform adaptif?"*
*   **Jawaban Akademis Anda:**
    > *"Sistem sekuensial diterapkan demi menjaga kualitas pedagogis dan keabsahan model Machine Learning:
    > 
    > 1. **Teori Scaffolding (Lev Vygotsky):** Pembelajaran berbasis komputer yang efektif harus dibangun secara bertahap dari konsep paling mendasar ke tingkat tersulit untuk menghindari **Cognitive Overload** (kebingungan informasi).
    > 2. **Integritas Data Model ML:** Jika semua bab dibuka sejak awal, siswa dapat mengklik acak semua materi tanpa membacanya. Hal ini akan mengotori data durasi belajar dengan *noise* (data palsu), yang mengakibatkan algoritma K-Means salah mengelompokkan profil gaya belajar siswa."*

---

### 5. Deteksi Perilaku "Gaming the System" (Klik Cepat & Gagal Kuis)

*   **Pertanyaan Penguji:**
    *"Bagaimana jika ada pengguna yang sengaja mengklik cepat seluruh slide materi (durasi belajar sangat rendah), lalu mencoba kuis berulang kali dengan cara menebak jawaban secara acak hingga lulus? Apakah model K-Means akan mendeteksinya sebagai Active Learner karena aktivitas kuisnya banyak?"*
*   **Jawaban Akademis Anda:**
    > *"Tidak. Algoritma K-Means akan mendeteksi perilaku ini sebagai **Gaming the System (Trial-and-Error Learner)** dan tetap mengelompokkannya ke dalam klaster **Passive Learner** (atau siswa yang membutuhkan bimbingan).
    > 
    > Secara matematis, K-Means mengevaluasi kontribusi seluruh fitur. Karena durasi belajar (`total_duration`) sangat rendah dan nilai rata-rata kuis (`avg_score`) juga sangat rendah akibat tebakan acak, koordinat siswa tersebut akan ditarik mendekati klaster Passive. 
    > 
    > Sistem adaptif AI kemudian akan merespons dengan memberikan rekomendasi berupa materi-materi tingkat dasar (*beginner*) untuk mengarahkan siswa kembali mempelajari materi fundamental terlebih dahulu."*

---
---

## 🛠️ BAGIAN B: JUSTIFIKASI KEAMANAN, DEPLOYMENT, REKAYASA DATA, & INFRASTRUKTUR

Berikut adalah kisi-kisi jawaban mengenai infrastruktur hosting, keamanan repositori GitHub, ketiadaan panel admin visual, serta metode rekayasa data siswa untuk kebutuhan skripsi:

### 6. Justifikasi Keamanan File Baru di Folder Terhubung Git/GitHub

*   **Pertanyaan Penguji / Pembimbing:**
    *"Apakah menambahkan berkas panduan baru di repositori lokal Anda akan merusak atau mengotori sistem yang sudah terhubung ke GitHub?"*
*   **Jawaban Teknis Anda:**
    > *"Tidak merusak sama sekali. Git bekerja menggunakan sistem pelacakan perubahan (*version control*). Menambahkan berkas dokumentasi baru (seperti di folder `dokumentasi/`) di luar folder utama program (`frontend` dan `backend`) hanya akan dideteksi oleh Git sebagai berkas **`untracked`** (hijau/U). 
    > 
    > Berkas ini tidak memengaruhi kode program utama yang sedang berjalan di produksi, dan perubahan baru akan dikirimkan ke GitHub secara aman hanya ketika dijalankan perintah `git add`, `git commit`, dan `git push` secara sadar."*

---

### 7. Justifikasi Ketiadaan UI Admin Panel Khusus

*   **Pertanyaan Penguji:**
    *"Mengapa di aplikasi Edusight Anda tidak terdapat antarmuka (UI) Admin Panel khusus untuk mengelola konten dan melihat progres siswa?"*
*   **Jawaban Akademis Anda:**
    > *"Aplikasi Edusight dirancang menggunakan prinsip **Separation of Concerns (Pemisahan Tanggung Jawab)** dan efisiensi arsitektur. 
    > 
    > Pengelolaan konten database dan aktivitas ekspor data hasil belajar siswa (format Excel/CSV) cukup dilakukan oleh administrator menggunakan **Swagger UI (Interactive API Docs)** di rute `/docs` backend yang telah dilindungi oleh protokol keamanan autentikasi token JWT. 
    > 
    > Desain ini meminimalkan celah keamanan (*attack surface*) di sisi frontend serta menghemat sumber daya pengembangan dengan memfokuskan antarmuka visual khusus untuk pengalaman belajar siswa (*Student-Centered Experience*)."*

---

### 8. Justifikasi Penambahan Data Pengguna Simulasi (Rekayasa Data Skripsi)

*   **Pertanyaan Penguji:**
    *"Bagaimana Anda menjustifikasi penambahan data puluhan siswa simulasi (rekayasa progres belajar) di database Anda sebagai bahan analisis skripsi?"*
*   **Jawaban Akademis Anda:**
    > *"Penambahan data siswa simulasi ini merupakan metode ilmiah yang sah dan umum dalam riset teknologi informasi, yang dikenal sebagai **Synthetic Data Generation (Pembuatan Data Sintetis)**. 
    > 
    > Justifikasinya adalah: Karena keterbatasan waktu penelitian lapangan untuk mengumpulkan ratusan siswa riil secara masif, data simulasi dibuat dengan memetakan variasi perilaku belajar nyata (seperti durasi belajar singkat/lama dan nilai kuis rendah/tinggi). 
    > 
    > Data sintetis ini berfungsi sebagai instrumen pengujian (*testing instrument*) untuk mengevaluasi akurasi performa algoritma K-Means Clustering dan responsivitas rekomendasi AI sebelum sistem dirilis secara luas."*

---

### 9. Justifikasi Kemudahan Melakukan Revisi Pasca-Deployment

*   **Pertanyaan Penguji:**
    *"Apakah sistem yang sudah Anda deploy ke Vercel dan Hugging Face ini masih bisa direvisi fiturnya di kemudian hari jika ada masukan dari penguji?"*
*   **Jawaban Teknis Anda:**
    > *"Sangat bisa. Arsitektur deployment Edusight menggunakan alur **CI/CD (Continuous Integration / Continuous Deployment)**. 
    > 
    > Setiap ada revisi fitur atau perbaikan bug di komputer lokal, pengembang cukup melakukan push perubahan tersebut ke GitHub. Server **Vercel** (untuk frontend) dan **Hugging Face** (untuk backend) akan otomatis mendeteksi perubahan tersebut, melakukan build ulang dalam hitungan detik di latar belakang, dan memperbarui sistem online secara otomatis tanpa memutus akses pengguna yang sedang aktif."*

---

### 10. Justifikasi Batas Akses Pengguna Bersamaan (Concurrent Users Limit)

*   **Pertanyaan Penguji:**
    *"Bagaimana batas kapasitas server aplikasi Anda jika diakses oleh banyak pengguna (misalnya 20 orang secara bersamaan)?"*
*   **Jawaban Teknis Anda:**
    > *"Aplikasi ini aman diakses oleh 20 orang secara bersamaan. Namun, karena berjalan di infrastruktur server gratisan (Hugging Face Spaces CPU Basic dan Supabase Free Tier), waktu respons akan melambat jika 20 orang tersebut memicu request berat secara bersama-sama (seperti melakukan generate analisis AI di waktu yang sama). 
    > 
    > Justifikasinya adalah: Untuk kebutuhan pengujian skala terbatas (*pilot testing*) pada penelitian skripsi, infrastruktur gratis ini sangat memadai dan ekonomis. Apabila aplikasi ini akan digunakan untuk skala besar (misal satu sekolah/nasional), maka server backend wajib ditingkatkan ke layanan VPS berbayar dan Supabase Pro Tier untuk meningkatkan performa konkurensi database."*

---

### 11. Justifikasi Jumlah Tabel Database yang Banyak (Normalisasi 3NF)

*   **Pertanyaan Penguji:**
    *"Saya melihat di Supabase ada banyak sekali tabel database (seperti `users`, `materials`, `learning_activity`, `quiz_log`, `completion_log`, dll). Apakah semua tabel ini benar-benar diperlukan dan berfungsi? Mengapa tidak disatukan saja agar lebih sedikit?"*
*   **Jawaban Akademis Anda:**
    > *"Ya, seluruh **12 tabel** di database Supabase tersebut berfungsi aktif dan saling terintegrasi. Struktur ini dirancang mengikuti kaidah **Third Normal Form (3NF) / Normalisasi Basis Data Tingkat 3** untuk menjamin integritas data, menghindari data ganda (*redundancy*), dan mencegah anomali data (*insert/update/delete anomalies*).
    > 
    > Secara arsitektur, tabel-tabel ini dibagi menjadi 3 kategori fungsional yang sangat jelas (*Separation of Concerns*):
    > 
    > 1.  **Entitas Master (Konten Pembelajaran):** 
    >     *   `users` (Data akun siswa).
    >     *   `learning_paths` (Daftar jalur kurikulum).
    >     *   `materials` (Daftar bab modul).
    >     *   `quizzes` & `quiz_questions` (Struktur kuis dan bank soal).
    > 2.  **Entitas Transaksi (Input Feature Engineering K-Means):**
    >     *   `user_progress` (Kontrol sekuensial bab yang terkunci/terbuka).
    >     *   `login_log` (Menyimpan data log login untuk menghitung frekuensi login).
    >     *   `learning_activity` (Menyimpan log waktu masuk-keluar untuk menghitung durasi belajar).
    >     *   `quiz_log` (Menyimpan riwayat percobaan dan perolehan skor kuis).
    >     *   `completion_log` (Menyimpan catatan sejarah bab yang telah tuntas diselesaikan).
    > 3.  **Entitas Hasil Analisis AI (Cache Insight & Rekomendasi):**
    >     *   `insight` (Penyimpanan klaster gaya belajar K-Means dan narasi dari Groq LLM).
    >     *   `recommendations` (Penyimpanan tautan rekomendasi belajar).
    > 
    > Jika tabel-tabel ini disatukan secara paksa (*de-normalisasi*), database akan menjadi sangat lambat saat mengkalkulasi fitur Machine Learning karena ukuran baris data yang membengkak, serta berisiko merusak relasi integritas referensial (*Foreign Key Constraints*) sistem."*


