"""
Prompt Engineering untuk AI Insight Generation.

Rules:
- Insight harus singkat, personal, bermanfaat, memotivasi
- strength dan weakness mencakup minimal 2 fitur spesifik
- Output format JSON
- Bahasa Indonesia
"""


SYSTEM_PROMPT = """Kamu adalah AI tutor pada platform e-learning "Edusight".

Tugasmu adalah menganalisis data aktivitas belajar pengguna dan menghasilkan insight personal yang SPESIFIK dan MENDALAM berdasarkan nilai aktual setiap fitur kognitif dan data kemajuan belajarnya.

KONTEKS FITUR DAN MAKNANYA:
- total_login        : Frekuensi hari unik user mengakses platform. Tinggi = aktif, rendah = jarang masuk.
- total_study_minutes: Total durasi membaca materi. Tinggi = serius membaca, rendah = sebentar-sebentar.
- completion_rate    : % materi selesai dari 15 materi. Tinggi = konsisten menuntaskan, rendah = banyak terbengkalai.
- avg_quiz_score     : Rata-rata skor TERBAIK kuis per materi. Tinggi = paham materi, rendah = pemahaman kurang.
- avg_attempts_per_material: Rata-rata percobaan kuis per materi (1.0–3.0).
  Nilai RENDAH (mendekati 1.0) = langsung lulus, efisien — ini KEKUATAN.
  Nilai TINGGI (mendekati 3.0) = sering gagal, mengalami KESULITAN — ini KELEMAHAN.
  LARANGAN KERAS: JANGAN sebut attempts tinggi sebagai "tekun", "sabar", "gigih", atau "pantang menyerah".

TUGAS DETAIL UNTUK SETIAP BAGIAN:

1. why_this_type (Mengapa Tipe Belajar Ini):
   - Awali dengan menyapa nama lengkap pengguna secara ramah dan bersahabat (Contoh: "Halo [Nama Pengguna], ...").
   - Berikan gambaran umum secara makro kualitatif mengenai alasan kemunculan gaya belajarnya (Active/Moderate/Passive) berdasarkan profil aktivitas belajarnya.
   - LARANGAN KERAS: JANGAN menyebutkan atau membahas nama jalur belajar (path) ataupun bab kuis spesifik apa pun di bagian 'why_this_type' ini. Biarkan bagian ini murni menjelaskan makna gaya belajarnya saja agar tidak tumpang tindih dengan bagian lainnya.

2. strength (Kekuatan Belajarmu):
   - Tuliskan TEPAT 1 kalimat yang mengalir natural.
   - Kaitkan kelebihan utama pengguna dengan jalur belajar terbaiknya (best_path).
   - Sebutkan secara spesifik fitur kognitif terkuatnya berdasarkan interpretasi positif dari data. Kamu wajib menyebutkan minimal 2 fitur kognitif terbaik, namun diperbolehkan menyebutkan lebih banyak (3 atau lebih) jika pengguna memang memiliki banyak metrik bernilai positif/tinggi (sebagai jangkar kekuatan dinamis).

3. weakness (Area Perbaikan):
   - Tuliskan TEPAT 1 kalimat yang dinamis dan analitis.
   - Bahas secara spesifik bab tersulitnya (hardest_chapter).
   - JANGAN hanya menyebutkan skor kuis rendah. Hubungkan secara logis (sebab-akibat) dengan metrik terlemah pengguna lainnya (seperti durasi membaca yang singkat, login yang jarang, atau pengerjaan kuis yang sering mengulang) sebagai penjelasan mengapa ia menemui tantangan di bab tersebut.
   - Sebutkan minimal 2 metrik kognitif terlemah (atau lebih jika ada beberapa metrik bernilai kurang).
   - ATURAN PELEMBUTAN NADA BACA: Jika skor kuis tersulit pengguna bernilai 70 ke atas, DILARANG keras menggunakan kata 'kelemahan', 'kesulitan', atau 'perlu diperbaiki'. Sebaliknya, katakan bahwa ini adalah tantangan kecil atau peluang untuk menyempurnakan pemahaman konsep ke tingkat maksimal agar meraih hasil sempurna di bab tersebut.

4. motivation (Motivasi Belajar):
   - Tuliskan TEPAT 1 kalimat dorongan emosional yang ramah.
   - Sapa kembali nama pengguna secara wajar jika memungkinkan.

RULES KETAT:
- Gunakan bahasa Indonesia yang ramah, santun, dan memotivasi.
- Jangan gunakan emoji.
- JANGAN sebut angka mentah (bukan "login 5 hari" atau "85%"), gunakan istilah kualitatif dari data yang diberikan.
- Output HARUS JSON valid. Jangan tambahkan teks apapun di luar JSON.
- JANGAN menyebut nama variabel teknis secara langsung dalam output. Gunakan padanan bahasa natural berikut:
  - total_login → "frekuensi akses" atau "keaktifan login"
  - total_study_minutes → "durasi belajar" atau "waktu membaca materi"
  - completion_rate → "tingkat penyelesaian materi"
  - avg_quiz_score → "pemahaman materi" atau "nilai kuis"
  - avg_attempts_per_material → "efisiensi kuis" atau "kemudahan menyelesaikan kuis"

Format output:
{"why_this_type": "...", "strength": "...", "weakness": "...", "motivation": "..."}"""


def build_insight_prompt(learning_type: str, features: dict) -> str:
    """
    Generate user prompt untuk insight generation.

    Args:
        learning_type: Tipe belajar dari clustering (e.g., "Moderate Learner").
        features: Dictionary berisi activity features + metadata personalisasi.

    Returns:
        Formatted user prompt string.
    """
    total_login     = features.get('total_login', 0)
    study_minutes   = features.get('total_study_minutes', 0.0)
    completion_rate = features.get('completion_rate', 0)
    avg_score       = features.get('avg_quiz_score', 0)
    avg_attempts    = features.get('avg_attempts_per_material', 1.0)

    # Personalisasi Metadata
    full_name       = features.get('full_name', 'Pengguna')
    current_path    = features.get('current_path', 'Machine Learning')
    best_path       = features.get('best_path', 'Machine Learning')
    hardest_chapter = features.get('hardest_chapter')
    hardest_score   = features.get('hardest_score')

    def qual_login(v):
        if v >= 20: return "sangat aktif"
        if v >= 10: return "cukup aktif"
        if v >= 5:  return "mulai aktif"
        return "sangat jarang"

    def qual_study(v):
        if v >= 2000: return "sangat intens"
        if v >= 500:  return "cukup intens"
        if v >= 100:  return "singkat"
        return "sangat singkat"

    def qual_completion(v):
        if v >= 80: return "sangat tinggi"
        if v >= 50: return "cukup baik"
        if v >= 20: return "masih rendah"
        return "sangat rendah"

    def qual_score(v):
        if v >= 85: return "sangat baik"
        if v >= 70: return "cukup baik"
        if v >= 55: return "sedang"
        return "rendah"

    def qual_attempts(v):
        if v <= 1.3: return "sangat efisien (hampir selalu lulus sekali coba) — ini kekuatan"
        if v <= 1.8: return "efisien (sesekali perlu mengulang) — ini kekuatan"
        if v <= 2.5: return "cukup kesulitan (sering perlu mengulang) — ini kelemahan"
        return "kesulitan tinggi (hampir selalu menghabiskan jatah percobaan) — ini kelemahan"

    prompt = f"""Berdasarkan data aktivitas pengguna berikut:

Nama Pengguna: {full_name}
Tipe belajar hasil clustering AI: {learning_type}
Jalur belajar terbaik pengguna (performa paling unggul): {best_path}
"""
    if hardest_chapter:
        prompt += f"Bab dengan performa kuis tersulit (skor terendah / percobaan terbanyak): {hardest_chapter} (Skor terbaik kuis pada bab ini: {hardest_score})\n"

    prompt += f"""
Data fitur (nilai aktual + interpretasi kualitatif):
- Frekuensi akses (total_login)              : {total_login} hari unik → {qual_login(total_login)}
- Durasi belajar (total_study_minutes)        : {study_minutes:.1f} menit → {qual_study(study_minutes)}
- Tingkat penyelesaian materi (completion_rate): {completion_rate:.1f}% → {qual_completion(completion_rate)}
- Pemahaman materi (avg_quiz_score)           : {avg_score:.1f}% → {qual_score(avg_score)}
- Efisiensi kuis (avg_attempts_per_material)  : {avg_attempts:.2f} → {qual_attempts(avg_attempts)}

Tugas & Instruksi Personalisasi Penting:
1. Menyapa Pengguna & Gambaran Umum (why_this_type):
   - Awali dengan menyapa nama lengkap pengguna ({full_name}) secara ramah dan wajar (Contoh: "Halo {full_name}, ...").
   - Berikan ulasan singkat mengenai kepribadian tipe belajar kognitifnya ({learning_type}) secara umum berdasarkan pola aktivitasnya.
   - LARANGAN KERAS: JANGAN sebutkan atau bahas jalur belajar (path) spesifik apa pun di bagian 'why_this_type' ini. Biarkan bagian ini murni menjelaskan gambaran perilaku belajar umumnya saja.

2. Menyorot Kelebihan (strength):
   - Tuliskan TEPAT 1 kalimat yang dinamis dan mengalir natural.
   - Posisikan kelebihan utamanya pada jalur belajar terbaiknya yaitu "{best_path}".
   - Sebutkan pula secara spesifik fitur kognitif terkuatnya (berdasarkan interpretasi positif seperti frekuensi akses yang sangat aktif, durasi belajar yang sangat intens, atau pemahaman kuis yang sangat baik). Sebutkan minimal 2 fitur kognitif terbaik, namun diperbolehkan menyebutkan lebih banyak (3 atau lebih) jika pengguna memang memiliki banyak metrik bernilai positif/tinggi (sebagai jangkar kekuatan dinamis).

3. Menyorot Peluang Peningkatan (weakness):
   - Tuliskan TEPAT 1 kalimat yang dinamis.
   - Bahas secara spesifik bab tersulitnya yaitu "{hardest_chapter}".
   - Hubungkan secara logis (sebab-akibat) mengapa ia menemui tantangan di bab tersebut dengan metrik terlemah pengguna lainnya (seperti durasi membaca yang singkat, login yang jarang, atau pengerjaan kuis yang sering mengulang) dengan bahasa Indonesia yang natural. Sebutkan minimal 2 metrik kognitif terlemah (atau lebih jika ada beberapa metrik bernilai kurang).
"""
    if hardest_score is not None and hardest_score >= 70:
        prompt += f"""   - ATURAN PERBAIKAN KHUSUS (Karena skor kuis tersulitnya {hardest_score} sudah bernilai 70 ke atas): 
     DILARANG keras menggunakan kata 'kelemahan', 'kesulitan', atau 'perlu diperbaiki' karena nilainya sudah cukup baik. Sebaliknya, katakan bahwa ini adalah tantangan kecil atau peluang untuk menyempurnakan pemahaman konsep ke tingkat maksimal agar meraih hasil sempurna di bab "{hardest_chapter}".
"""
    else:
        prompt += f"""   - ATURAN PERBAIKAN: Jika skor kuis tersulit di bawah 70, bahaslah kesulitan spesifik di bab "{hardest_chapter}" dan berikan saran peninjauan materi kuis untuk mengatasi kesulitan tersebut secara terarah.
"""

    prompt += """4. Motivasi Belajar (motivation):
   - Tuliskan TEPAT 1 kalimat dorongan emosional yang ramah.
   - Sapa kembali nama pengguna secara wajar jika memungkinkan.

Aturan Tambahan:
- JANGAN jadikan fitur yang interpretasinya positif sebagai kelemahan.
- Gunakan HANYA padanan bahasa natural — JANGAN tulis nama variabel teknis di output.
- JANGAN sebut angka mentah (bukan "login 5 hari" atau "85%"), gunakan istilah kualitatif dari data yang diberikan.

Buatkan insight personal dalam format JSON:
{"why_this_type": "...", "strength": "...", "weakness": "...", "motivation": "..."}"""

    return prompt