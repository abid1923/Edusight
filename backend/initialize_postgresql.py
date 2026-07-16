"""
PostgreSQL Initialization and Seeding Script.
Creates tables and seeds initial data to Supabase.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine
from seed import run_seed
from seed_test_user import seed_test_user

def main():
    print("=" * 60)
    print("INITIALIZING POSTGRESQL DATABASE (SUPABASE)")
    print("=" * 60)
    
    # 1. Create all tables on PostgreSQL
    print("[*] Creating database schema/tables in Supabase...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] All database tables successfully created in Supabase!")
    except Exception as e:
        print(f"[FAIL] Error creating tables: {e}")
        sys.exit(1)
        
    # 2. Run Seeders
    print("\n[*] Running seeders...")
    try:
        # Seed paths, materials and quizzes
        run_seed()
        
        # Seed testuser and researchadmin
        print("\n[*] Seeding test user and admin account...")
        seed_test_user()
        
        print("\n[OK] Seeding complete!")
    except Exception as e:
        print(f"[FAIL] Error running seeders: {e}")
        sys.exit(1)
        
    print("=" * 60)
    print("POSTGRESQL MIGRATION INITIALIZATION SUCCESSFUL!")
    print("=" * 60)

if __name__ == "__main__":
    main()
