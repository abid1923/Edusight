"""
Seed database using real content from JSON files.
Aligns learning paths, materials, quizzes, and quiz questions with the JSON content.
Run: python seed_real_data.py
"""

import os
import sys
import json
from datetime import datetime, timezone

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models.user_model import User
from app.models.activity_model import LearningPath, Material, Quiz, QuizQuestion, QuizAttempt, UserProgress
from app.models.logging_model import LoginLog, LearningActivity, QuizLog, CompletionLog
from app.models.insight_model import Insight, Recommendation

def run_seed_real():
    db = SessionLocal()
    print("[*] Starting database seeding from JSON content...")

    # Order of deletion to avoid foreign key constraints
    print("[*] Clearing existing learning data from database...")
    db.query(Recommendation).delete()
    db.query(Insight).delete()
    db.query(CompletionLog).delete()
    db.query(QuizLog).delete()
    db.query(LearningActivity).delete()
    db.query(QuizAttempt).delete()
    db.query(UserProgress).delete()
    db.query(QuizQuestion).delete()
    db.query(Quiz).delete()
    db.query(Material).delete()
    db.query(LearningPath).delete()
    db.commit()
    print("[OK] Cleared old data.")

    # Paths configuration
    # Maps learning path name -> (order, folder_materi, folder_kuis, file_prefix_materi, file_suffix_materi, file_suffix_kuis)
    paths_config = {
        "Machine Learning": {
            "order": 1,
            "desc": "Pelajari dasar-dasar Machine Learning, dari konsep hingga implementasi model.",
            "materi_folder": "materi path machine learning",
            "kuis_folder": "kuis machine learning",
            "materi_files": {
                1: "bab 1/ml_bab1_dasar_ml_materi.json",
                2: "bab 2/ml_bab2_supervised_materi.json",
                3: "bab 3/ml_bab3_unsupervised_materi.json",
                4: "bab 4/ml_bab4_deeplearning_materi.json",
                5: "bab 5/ml_bab5_deployment_mlops_materi.json"
            },
            "kuis_files": {
                1: "bab1_ml_kuis.json",
                2: "bab2_ml_kuis.json",
                3: "bab3_ml_kuis.json",
                4: "bab4_ml_kuis.json",
                5: "bab5_ml_kuis.json"
            }
        },
        "Frontend Development": {
            "order": 2,
            "desc": "Kuasai pengembangan antarmuka web modern dengan HTML, CSS, dan JavaScript.",
            "materi_folder": "materi path front end",
            "kuis_folder": "kuis front end",
            "materi_files": {
                1: "bab 1/FE_bab1_dasar_html_materi.json",
                2: "bab 2/FE_bab2_css_materi.json",
                3: "bab 3/FE_bab3_javascript_materi.json",
                4: "bab 4/FE_bab4_dom_event_materi.json",
                5: "bab 5/FE_bab5_react_materi.json"
            },
            "kuis_files": {
                1: "bab1_dasar_html_kuis.json",
                2: "bab2_css_kuis.json",
                3: "bab3_javascript_kuis.json",
                4: "bab4_dom_event_kuis.json",
                5: "bab5_react_kuis.json"
            }
        },
        "Backend Development": {
            "order": 3,
            "desc": "Kuasai pembuatan server, API, dan pengelolaan database menggunakan Node.js dan Express.",
            "materi_folder": "materi path backend",
            "kuis_folder": "kuis back end",
            "materi_files": {
                1: "bab 1/backend_bab1_nodejs_materi.json",
                2: "bab 2/backend_bab2_express_materi.json",
                3: "bab 3/backend_bab3_sql_materi.json",
                4: "bab 4/backend_bab4_mongodb_materi.json",
                5: "bab 5/backend_bab5_auth_materi.json"
            },
            "kuis_files": {
                1: "backend_bab1_nodejs_kuis.json",
                2: "backend_bab2_express_kuis.json",
                3: "backend_bab3_sql_kuis.json",
                4: "backend_bab4_mongodb_kuis.json",
                5: "backend_bab5_auth_kuis.json"
            }
        }
    }

    base_content_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/public/content"))

    for path_name, config in paths_config.items():
        print(f"\n[*] Seeding Learning Path: {path_name}")
        lp = LearningPath(
            name=path_name,
            description=config["desc"],
            order=config["order"]
        )
        db.add(lp)
        db.flush()  # Acquire lp.id

        for bab in range(1, 6):
            # 1. Load Material JSON to get real title and description
            materi_rel_path = f"materi/{config['materi_folder']}/{config['materi_files'][bab]}"
            materi_full_path = os.path.join(base_content_path, materi_rel_path)
            
            if not os.path.exists(materi_full_path):
                print(f"[ERROR] Material file not found: {materi_full_path}")
                continue

            with open(materi_full_path, "r", encoding="utf-8") as f:
                materi_data = json.load(f)

            meta = materi_data.get("meta", {})
            judul_bab = meta.get("judul_bab", f"Bab {bab}")
            deskripsi_bab = meta.get("deskripsi", "")

            print(f"   - Seeding Material {bab}: {judul_bab}")
            mat = Material(
                learning_path_id=lp.id,
                title=judul_bab,
                description=deskripsi_bab,
                order=bab
            )
            db.add(mat)
            db.flush()  # Acquire mat.id

            # 2. Load Quiz JSON and seed Quiz + Questions
            kuis_rel_path = f"kuis/{config['kuis_folder']}/{config['kuis_files'][bab]}"
            kuis_full_path = os.path.join(base_content_path, kuis_rel_path)

            if not os.path.exists(kuis_full_path):
                print(f"[ERROR] Quiz file not found: {kuis_full_path}")
                continue

            with open(kuis_full_path, "r", encoding="utf-8") as f:
                kuis_data = json.load(f)

            quiz_meta = kuis_data.get("meta", {})
            quiz_title = f"Quiz: {judul_bab}"

            quiz = Quiz(
                material_id=mat.id,
                title=quiz_title
            )
            db.add(quiz)
            db.flush()  # Acquire quiz.id

            questions_list = kuis_data.get("soal", [])
            for q_data in questions_list:
                # Opsi is a dictionary with A, B, C, D keys
                opsi = q_data.get("opsi", {})
                q_text = q_data.get("pertanyaan", "")
                correct = q_data.get("jawaban", "A").lower()

                q_obj = QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q_text,
                    option_a=opsi.get("A", ""),
                    option_b=opsi.get("B", ""),
                    option_c=opsi.get("C", ""),
                    option_d=opsi.get("D", ""),
                    correct_answer=correct
                )
                db.add(q_obj)

    db.commit()
    print("\n[OK] Seeding complete from JSON files!")
    print(f"   - {db.query(LearningPath).count()} learning paths")
    print(f"   - {db.query(Material).count()} materials")
    print(f"   - {db.query(Quiz).count()} quizzes")
    print(f"   - {db.query(QuizQuestion).count()} quiz questions")
    db.close()

if __name__ == "__main__":
    run_seed_real()
