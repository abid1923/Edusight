import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models.user_model import User
from app.models.activity_model import Material
from app.models.insight_model import Insight
from app.models.logging_model import LoginLog, QuizLog, CompletionLog, LearningActivity

def seed_test_user():
    db = SessionLocal()
    
    # 1. Create Normal Test User
    email = "test@example.com"
    user = db.query(User).filter(User.email == email).first()
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    if not user:
        user = User(
            username="testuser",
            email=email,
            hashed_password=pwd_context.hash("password123"),
            full_name="Test User",
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.username} (ID: {user.id})")
    else:
        user.is_admin = False
        db.commit()
        print(f"User testuser already exists (ID: {user.id}). Ensured is_admin=False.")

    # 1b. Create Admin Test User
    admin_email = "admin@example.com"
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            username="researchadmin",
            email=admin_email,
            hashed_password=pwd_context.hash("password123"),
            full_name="Research Administrator",
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Created admin user: {admin_user.username} (ID: {admin_user.id})")
    else:
        # Make sure is_admin is True even if they exist
        admin_user.is_admin = True
        db.commit()
        print(f"Admin user researchadmin already exists (ID: {admin_user.id}). Ensured is_admin=True.")
        
    user_id = user.id
    now = datetime.now()
    
    # 2. Add 5 login logs
    logins_count = db.query(LoginLog).filter(LoginLog.user_id == user_id).count()
    if logins_count < 5:
        for i in range(5 - logins_count):
            db.add(LoginLog(user_id=user_id, timestamp=now - timedelta(days=i)))
        print(f"Added {5 - logins_count} login logs")
            
    # 3. Add 3 quiz logs
    quizzes_count = db.query(QuizLog).filter(QuizLog.user_id == user_id).count()
    if quizzes_count < 3:
        for i in range(3 - quizzes_count):
            db.add(QuizLog(
                user_id=user_id, 
                material_id=1, 
                path="Machine Learning", 
                score=80, 
                attempt=1, 
                timestamp=now - timedelta(days=i)
            ))
        print(f"Added {3 - quizzes_count} quiz logs")
            
    # 4. Add 2 completion logs
    completions_count = db.query(CompletionLog).filter(CompletionLog.user_id == user_id).count()
    if completions_count < 2:
        for i in range(2 - completions_count):
            db.add(CompletionLog(
                user_id=user_id,
                material_id=i+1,
                path="Machine Learning",
                completed_at=now - timedelta(days=i)
            ))
        print(f"Added {2 - completions_count} completion logs")
            
    db.commit()
    db.close()
    print("Seed test user done.")

if __name__ == "__main__":
    seed_test_user()
