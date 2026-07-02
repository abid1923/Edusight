import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user_model import User
from app.ai.feature_engineering import extract_features
from app.ai.inference import predict_learning_type, load_model
# Make sure model classes are imported so SQLAlchemy resolver doesn't throw errors
from app.models.insight_model import Insight, Recommendation

def query_simulation_features():
    # Load AI models
    load_model()
    
    db = SessionLocal()
    usernames = ["ardinugraha", "sitirahayu", "budisantoso"]
    
    print("=" * 60)
    print("ACTUAL FEATURES & CLUSTERING RESULTS FOR SIMULATION USERS")
    print("=" * 60)
    
    for username in usernames:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User {username} not found in database!")
            continue
            
        features = extract_features(user.id, db)
        print(f"\nUser: {username} (ID: {user.id})")
        print("-" * 30)
        for k, v in features.items():
            print(f"* {k} = {v}")
            
        try:
            prediction = predict_learning_type(user.id, db)
            print(f"* cluster_id = {prediction['cluster_id']}")
            print(f"* learning_type = {prediction['learning_type']}")
        except Exception as e:
            print(f"Clustering prediction failed for {username}: {e}")
            
    db.close()
    print("=" * 60)

if __name__ == "__main__":
    query_simulation_features()
