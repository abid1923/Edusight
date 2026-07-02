"""
Database seed script.
Populates learning paths, materials, and quiz questions.
Run: python seed.py
"""

import sys
import os
import json

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models.user_model import User
from app.models.activity_model import LearningPath, Material, Quiz, QuizQuestion, QuizAttempt, UserProgress
from app.models.insight_model import Insight
from app.models.logging_model import LoginLog, LearningActivity, QuizLog, CompletionLog

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()


def seed_learning_paths():
    """Seed 3 learning paths."""
    paths = [
        LearningPath(name="Machine Learning", description="Pelajari dasar-dasar Machine Learning, dari konsep hingga implementasi model.", order=1),
        LearningPath(name="Frontend Development", description="Kuasai pengembangan antarmuka web modern dengan HTML, CSS, dan JavaScript.", order=2),
        LearningPath(name="Backend Development", description="Kuasai pembuatan server, API, dan pengelolaan database menggunakan Node.js dan Express.", order=3),
    ]
    for p in paths:
        existing = db.query(LearningPath).filter(LearningPath.name == p.name).first()
        if not existing:
            db.add(p)
        else:
            existing.description = p.description
    db.commit()
    print("[OK] Learning paths seeded")


def seed_materials():
    """Seed 5 materials per learning path (15 total) from local JSON files."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public"))
    mats_map = {
        "Machine Learning": {
            1: "content/materi/materi path machine learning/bab 1/ml_bab1_dasar_ml_materi.json",
            2: "content/materi/materi path machine learning/bab 2/ml_bab2_supervised_materi.json",
            3: "content/materi/materi path machine learning/bab 3/ml_bab3_unsupervised_materi.json",
            4: "content/materi/materi path machine learning/bab 4/ml_bab4_deeplearning_materi.json",
            5: "content/materi/materi path machine learning/bab 5/ml_bab5_deployment_mlops_materi.json"
        },
        "Frontend Development": {
            1: "content/materi/materi path front end/bab 1/FE_bab1_dasar_html_materi.json",
            2: "content/materi/materi path front end/bab 2/FE_bab2_css_materi.json",
            3: "content/materi/materi path front end/bab 3/FE_bab3_javascript_materi.json",
            4: "content/materi/materi path front end/bab 4/FE_bab4_dom_event_materi.json",
            5: "content/materi/materi path front end/bab 5/FE_bab5_react_materi.json"
        },
        "Backend Development": {
            1: "content/materi/materi path backend/bab 1/backend_bab1_nodejs_materi.json",
            2: "content/materi/materi path backend/bab 2/backend_bab2_express_materi.json",
            3: "content/materi/materi path backend/bab 3/backend_bab3_sql_materi.json",
            4: "content/materi/materi path backend/bab 4/backend_bab4_mongodb_materi.json",
            5: "content/materi/materi path backend/bab 5/backend_bab5_auth_materi.json"
        }
    }

    for path_name, babs in mats_map.items():
        path = db.query(LearningPath).filter(LearningPath.name == path_name).first()
        if not path:
            continue
        for order, rel_path in babs.items():
            full_path = os.path.join(base_dir, rel_path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    meta = data.get("meta", {})
                    title = meta.get("judul_bab")
                    desc = meta.get("deskripsi")
            else:
                title = f"Material {order}"
                desc = "Placeholder description"

            existing = db.query(Material).filter(Material.learning_path_id == path.id, Material.order == order).first()
            if not existing:
                db.add(Material(learning_path_id=path.id, title=title, description=desc, order=order))
            else:
                existing.title = title
                existing.description = desc
    db.commit()
    print("[OK] Materials seeded")


def seed_quizzes():
    """Seed a quiz with questions per material (from local JSON files)."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public"))
    quiz_map = {
        "Machine Learning": {
            1: "content/kuis/kuis machine learning/bab1_ml_kuis.json",
            2: "content/kuis/kuis machine learning/bab2_ml_kuis.json",
            3: "content/kuis/kuis machine learning/bab3_ml_kuis.json",
            4: "content/kuis/kuis machine learning/bab4_ml_kuis.json",
            5: "content/kuis/kuis machine learning/bab5_ml_kuis.json"
        },
        "Frontend Development": {
            1: "content/kuis/kuis front end/bab1_dasar_html_kuis.json",
            2: "content/kuis/kuis front end/bab2_css_kuis.json",
            3: "content/kuis/kuis front end/bab3_javascript_kuis.json",
            4: "content/kuis/kuis front end/bab4_dom_event_kuis.json",
            5: "content/kuis/kuis front end/bab5_react_kuis.json"
        },
        "Backend Development": {
            1: "content/kuis/kuis back end/backend_bab1_nodejs_kuis.json",
            2: "content/kuis/kuis back end/backend_bab2_express_kuis.json",
            3: "content/kuis/kuis back end/backend_bab3_sql_kuis.json",
            4: "content/kuis/kuis back end/backend_bab4_mongodb_kuis.json",
            5: "content/kuis/kuis back end/backend_bab5_auth_kuis.json"
        }
    }

    materials = db.query(Material).all()

    for mat in materials:
        path = db.query(LearningPath).filter(LearningPath.id == mat.learning_path_id).first()
        rel_path = quiz_map.get(path.name, {}).get(mat.order)
        if not rel_path:
            continue
        
        full_path = os.path.join(base_dir, rel_path)
        
        existing_quiz = db.query(Quiz).filter(Quiz.material_id == mat.id).first()
        if existing_quiz:
            quiz = existing_quiz
            quiz.title = f"Quiz: {mat.title}"
        else:
            quiz = Quiz(material_id=mat.id, title=f"Quiz: {mat.title}")
            db.add(quiz)
            db.flush()

        # Delete existing questions
        db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).delete()

        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                questions = data.get("soal", [])
            for q in questions:
                db.add(QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q["pertanyaan"],
                    option_a=q["opsi"]["A"],
                    option_b=q["opsi"]["B"],
                    option_c=q["opsi"]["C"],
                    option_d=q["opsi"]["D"],
                    correct_answer=q["jawaban"].lower(),
                ))
        else:
            # Fallback placeholder questions
            placeholder_qs = _default_questions(mat.title)
            for q_data in placeholder_qs[:10]:
                db.add(QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q_data["q"],
                    option_a=q_data["a"],
                    option_b=q_data["b"],
                    option_c=q_data["c"],
                    option_d=q_data["d"],
                    correct_answer=q_data["answer"],
                ))

    db.commit()
    print("[OK] Quizzes seeded")


def _default_questions(title):
    """Generate 10 generic placeholder questions for any material."""
    return [
        {"q": f"Apa tujuan utama dari {title}?", "a": "Memahami konsep dasar", "b": "Menghafal rumus", "c": "Menyelesaikan tugas", "d": "Membaca buku", "answer": "a"},
        {"q": f"Manakah yang BUKAN termasuk topik dalam {title}?", "a": "Konsep dasar", "b": "Implementasi", "c": "Memasak", "d": "Evaluasi", "answer": "c"},
        {"q": f"Mengapa {title} penting dalam pengembangan software?", "a": "Tidak penting", "b": "Meningkatkan kualitas produk", "c": "Menambah biaya", "d": "Mengurangi fitur", "answer": "b"},
        {"q": f"Apa langkah pertama dalam mempelajari {title}?", "a": "Langsung coding", "b": "Memahami teori dasar", "c": "Membuat proyek besar", "d": "Skip materi", "answer": "b"},
        {"q": f"Tools apa yang umum digunakan dalam {title}?", "a": "Notepad saja", "b": "IDE dan framework modern", "c": "Kalkulator", "d": "Microsoft Word", "answer": "b"},
        {"q": f"Bagaimana cara terbaik berlatih {title}?", "a": "Hanya membaca", "b": "Practice dan project", "c": "Menghafal", "d": "Tidak perlu latihan", "answer": "b"},
        {"q": f"Apa output yang diharapkan dari mempelajari {title}?", "a": "Tidak ada output", "b": "Mampu mengimplementasikan konsep", "c": "Sertifikat saja", "d": "Nilai tinggi saja", "answer": "b"},
        {"q": f"Siapa yang cocok mempelajari {title}?", "a": "Hanya expert", "b": "Semua level learner", "c": "Hanya mahasiswa", "d": "Hanya profesional", "answer": "b"},
        {"q": f"Apa tantangan utama dalam {title}?", "a": "Tidak ada tantangan", "b": "Memahami konsep abstrak", "c": "Terlalu mudah", "d": "Tidak perlu effort", "answer": "b"},
        {"q": f"Bagaimana mengukur keberhasilan belajar {title}?", "a": "Tidak bisa diukur", "b": "Quiz dan project implementation", "c": "Jumlah halaman dibaca", "d": "Waktu yang dihabiskan saja", "answer": "b"},
    ]


def _generate_quiz_bank():
    """Generate topic-specific questions for key materials."""
    return {
        "Pengenalan Machine Learning": [
            {"q": "Apa itu Machine Learning?", "a": "Cabang AI yang memungkinkan komputer belajar dari data", "b": "Software antivirus", "c": "Bahasa pemrograman", "d": "Database system", "answer": "a"},
            {"q": "Manakah yang termasuk jenis Machine Learning?", "a": "Supervised Learning", "b": "Manual Learning", "c": "Paper Learning", "d": "Book Learning", "answer": "a"},
            {"q": "Apa perbedaan supervised dan unsupervised learning?", "a": "Tidak ada perbedaan", "b": "Supervised menggunakan label, unsupervised tidak", "c": "Unsupervised lebih akurat", "d": "Supervised tidak menggunakan data", "answer": "b"},
            {"q": "Contoh aplikasi ML di kehidupan sehari-hari?", "a": "Rekomendasi Netflix", "b": "Kalkulator biasa", "c": "Lampu lalu lintas manual", "d": "Buku cetak", "answer": "a"},
            {"q": "Library Python yang populer untuk ML?", "a": "Django", "b": "Scikit-learn", "c": "Flask", "d": "Tkinter", "answer": "b"},
            {"q": "Apa itu training data?", "a": "Data untuk melatih model ML", "b": "Data untuk testing saja", "c": "Data yang tidak digunakan", "d": "Data yang dihapus", "answer": "a"},
            {"q": "Apa itu overfitting?", "a": "Model terlalu sederhana", "b": "Model terlalu cocok dengan training data", "c": "Model tidak belajar", "d": "Model rusak", "answer": "b"},
            {"q": "Feature dalam ML adalah?", "a": "Variabel input untuk model", "b": "Output model", "c": "Error model", "d": "Nama model", "answer": "a"},
            {"q": "Apa tujuan evaluasi model?", "a": "Mengukur performa model", "b": "Menghapus model", "c": "Membuat model baru", "d": "Mengabaikan hasil", "answer": "a"},
            {"q": "Deep Learning adalah subset dari?", "a": "Web Development", "b": "Machine Learning", "c": "Database", "d": "Networking", "answer": "b"},
        ],
        "HTML Fundamentals": [
            {"q": "Apa kepanjangan HTML?", "a": "HyperText Markup Language", "b": "High Tech Modern Language", "c": "Home Tool Markup Language", "d": "Hyperlink Text Machine Language", "answer": "a"},
            {"q": "Tag untuk heading terbesar di HTML?", "a": "<h6>", "b": "<h1>", "c": "<header>", "d": "<head>", "answer": "b"},
            {"q": "Tag untuk membuat paragraf?", "a": "<paragraph>", "b": "<text>", "c": "<p>", "d": "<para>", "answer": "c"},
            {"q": "Atribut untuk menambahkan link di tag <a>?", "a": "src", "b": "link", "c": "href", "d": "url", "answer": "c"},
            {"q": "Tag untuk membuat list tidak berurutan?", "a": "<ol>", "b": "<ul>", "c": "<list>", "d": "<dl>", "answer": "b"},
            {"q": "Apa fungsi tag <div>?", "a": "Container/pembungkus elemen", "b": "Membuat tabel", "c": "Menambahkan gambar", "d": "Membuat link", "answer": "a"},
            {"q": "Tag semantic untuk navigasi?", "a": "<div>", "b": "<nav>", "c": "<span>", "d": "<menu>", "answer": "b"},
            {"q": "Cara menambahkan gambar di HTML?", "a": "<image>", "b": "<picture>", "c": "<img>", "d": "<photo>", "answer": "c"},
            {"q": "Apa itu HTML5?", "a": "Versi terbaru HTML", "b": "Library JavaScript", "c": "CSS framework", "d": "Database", "answer": "a"},
            {"q": "Tag untuk membuat form input?", "a": "<form>", "b": "<input-form>", "c": "<data>", "d": "<entry>", "answer": "a"},
        ],
        "Python Fundamentals": [
            {"q": "Python adalah bahasa pemrograman bertipe?", "a": "Compiled only", "b": "Interpreted", "c": "Assembly", "d": "Machine code", "answer": "b"},
            {"q": "Cara mendeklarasikan variabel di Python?", "a": "var x = 10", "b": "int x = 10", "c": "x = 10", "d": "let x = 10", "answer": "c"},
            {"q": "Tipe data untuk teks di Python?", "a": "int", "b": "str", "c": "char", "d": "text", "answer": "b"},
            {"q": "Cara membuat function di Python?", "a": "function nama():", "b": "def nama():", "c": "func nama():", "d": "fn nama():", "answer": "b"},
            {"q": "Apa itu list di Python?", "a": "Tipe data terurut yang bisa diubah", "b": "Tipe data yang tidak bisa diubah", "c": "Hanya untuk angka", "d": "Hanya untuk teks", "answer": "a"},
            {"q": "Cara menulis komentar di Python?", "a": "// komentar", "b": "# komentar", "c": "/* komentar */", "d": "-- komentar", "answer": "b"},
            {"q": "Apa output dari print(type(3.14))?", "a": "<class 'int'>", "b": "<class 'float'>", "c": "<class 'str'>", "d": "<class 'double'>", "answer": "b"},
            {"q": "Cara membuat loop di Python?", "a": "foreach i in range:", "b": "for i in range(10):", "c": "loop i to 10:", "d": "repeat 10:", "answer": "b"},
            {"q": "Apa itu dictionary di Python?", "a": "Koleksi key-value pairs", "b": "Kamus bahasa", "c": "List of numbers", "d": "Tipe data boolean", "answer": "a"},
            {"q": "Cara import modul di Python?", "a": "require('modul')", "b": "import modul", "c": "#include modul", "d": "using modul", "answer": "b"},
        ],
    }


def run_seed():
    """Run all seed functions."""
    print("[*] Seeding database...")
    seed_learning_paths()
    seed_materials()
    seed_quizzes()
    print("[OK] Database seeding complete!")
    print(f"   - {db.query(LearningPath).count()} learning paths")
    print(f"   - {db.query(Material).count()} materials")
    print(f"   - {db.query(Quiz).count()} quizzes")
    print(f"   - {db.query(QuizQuestion).count()} quiz questions")
    print("")
    print("[*] Database tables created:")
    print("   - users")
    print("   - learning_paths")
    print("   - materials")
    print("   - quizzes")
    print("   - quiz_questions")
    print("   - quiz_attempts")
    print("   - user_progress")
    print("   - login_log          (AI dataset)")
    print("   - learning_activity  (AI dataset)")
    print("   - quiz_log           (AI dataset)")
    print("   - completion_log     (AI dataset)")
    print("   - insights           (AI dataset)")


if __name__ == "__main__":
    run_seed()
    db.close()
