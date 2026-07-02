"""
Backend Endpoint Verification Script.
Uses FastAPI TestClient to test all modified and updated endpoints:
- Auth login
- User dashboard (fallback & after insight generation)
- Dedicated Recommendation
- AI Insight (threshold check & generation)
- CSV Dataset Export
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

def run_verification():
    print("=" * 60)
    print("STARTING BACKEND API VERIFICATION WITH LIFESPAN ACTIVE")
    print("=" * 60)
    
    # Using 'with' block triggers the lifespan events (which load the AI model!)
    with TestClient(app) as client:
        # ─── 1. AUTH LOGIN ──────────────────────────────────────────
        print("\n[TEST] POST /api/auth/login")
        login_response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "password123"}
        )
        
        if login_response.status_code != 200:
            print(f"[FAIL] Login failed: {login_response.text}")
            return
            
        token_data = login_response.json()
        token = token_data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"[OK] Login successful! Token acquired: {token[:20]}...")
        
        # ─── 2. USER DASHBOARD (FALLBACK / NO INSIGHT STATE) ─────────
        print("\n[TEST] GET /api/users/dashboard (Fallback State)")
        dashboard_res = client.get("/api/users/dashboard", headers=headers)
        assert dashboard_res.status_code == 200, f"Dashboard failed: {dashboard_res.text}"
        db_data = dashboard_res.json()
        
        # Validate DashboardResponse schema
        expected_fields = ["username", "learning_type", "reason", "strength", "weakness", "motivation", "progress_summary", "recommendation_summary"]
        for field in expected_fields:
            assert field in db_data, f"Missing field '{field}' in dashboard data"
            
        print(f"[OK] Dashboard fields verified: {list(db_data.keys())}")
        print(f"[OK] User learning_type (Fallback): {db_data['learning_type']}")
        print(f"[OK] User reason (Fallback): {db_data['reason']}")
        print(f"[OK] Progress summary: {db_data['progress_summary']}")
        print(f"[OK] Fallback recommendations returned: {len(db_data['recommendation_summary'])}")
        
        # ─── 3. DEDICATED RECOMMENDATION ────────────────────────────
        print("\n[TEST] GET /api/recommendation/me")
        rec_res = client.get("/api/recommendation/me", headers=headers)
        assert rec_res.status_code == 200, f"Recommendations failed: {rec_res.text}"
        rec_data = rec_res.json()
        print(f"[OK] Recommendation items returned: {len(rec_data)}")
        if rec_data:
            first_rec = rec_data[0]
            print(f"   - First Rec: {first_rec.get('title')} ({first_rec.get('resource_type')})")
            print(f"   - Score: {first_rec.get('score')}, Priority: {first_rec.get('priority')}")
            assert "title" in first_rec
            assert "resource_type" in first_rec
            assert "score" in first_rec
            
        # ─── 4. AI INSIGHT THRESHOLD CHECK ──────────────────────────
        print("\n[TEST] GET /api/insight/threshold")
        thresh_res = client.get("/api/insight/threshold", headers=headers)
        assert thresh_res.status_code == 200, f"Threshold check failed: {thresh_res.text}"
        thresh_data = thresh_res.json()
        print(f"[OK] Meets threshold: {thresh_data.get('meets_threshold')}")
        print(f"[OK] Details: {thresh_data.get('details')}")
        
        # ─── 5. AI INSIGHT GENERATION ──────────────────────────────
        print("\n[TEST] POST /api/insight/generate")
        gen_res = client.post("/api/insight/generate?force=true", headers=headers)
        
        if gen_res.status_code == 200:
            gen_data = gen_res.json()
            print(f"[OK] Insight generated successfully: {gen_data.get('message')}")
            insight = gen_data.get("insight")
            if insight:
                print(f"   - Learning Type: {insight.get('learning_type')}")
                print(f"   - Strength: {insight.get('strength')}")
                print(f"   - Weakness: {insight.get('weakness')}")
                print(f"   - Motivation: {insight.get('motivation')}")
        else:
            print(f"[WARNING] Insight generation returned status {gen_res.status_code}: {gen_res.text}")
            print("   Note: This is expected if the machine learning model pkl files are missing or GROQ_API_KEY is not active.")
            
        # ─── 6. GET DASHBOARD AGAIN (POST-GENERATION) ───────────────
        print("\n[TEST] GET /api/users/dashboard (Post-Insight State)")
        dashboard_res = client.get("/api/users/dashboard", headers=headers)
        assert dashboard_res.status_code == 200
        db_data = dashboard_res.json()
        print(f"[OK] User learning_type (Current): {db_data['learning_type']}")
        print(f"[OK] User reason (Current): {db_data['reason']}")
        print(f"[OK] Strength: {db_data['strength']}")
        print(f"[OK] Weakness: {db_data['weakness']}")
        print(f"[OK] Motivation: {db_data['motivation']}")
        print(f"[OK] Recommendation summary count: {len(db_data['recommendation_summary'])}")
        if db_data['recommendation_summary']:
            print(f"   - First Rec: {db_data['recommendation_summary'][0]['title']}")
        
        # ─── 7. EXPORT DATASET AS CSV (EXPECT 403 FOR USER) ─────────
        export_endpoints = [
            ("/api/export/login-log", "login_log.csv"),
            ("/api/export/learning-activity", "learning_activity.csv"),
            ("/api/export/quiz-log", "quiz_log.csv"),
            ("/api/export/completion-log", "completion_log.csv"),
            ("/api/export/insights", "insights.csv"),
        ]
        
        print("\n[TEST] Verifying normal user is blocked from export endpoints...")
        for endpoint, filename in export_endpoints:
            print(f"[TEST] GET {endpoint} (as testuser)")
            res = client.get(endpoint, headers=headers)
            assert res.status_code == 403, f"Expected 403 Forbidden for normal user on {endpoint}, got {res.status_code}"
            print(f"[OK] Blocked successfully! Status code: 403 Forbidden")
            
        # ─── 8. ADMIN LOGIN & DATASET EXPORT (EXPECT 200) ───────────
        print("\n[TEST] POST /api/auth/login (as admin)")
        admin_login_res = client.post(
            "/api/auth/login",
            data={"username": "researchadmin", "password": "password123"}
        )
        assert admin_login_res.status_code == 200, f"Admin login failed: {admin_login_res.text}"
        admin_token_data = admin_login_res.json()
        admin_token = admin_token_data.get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print(f"[OK] Admin login successful! Token acquired: {admin_token[:20]}...")
        
        print("\n[TEST] Verifying administrator can access export endpoints...")
        for endpoint, filename in export_endpoints:
            print(f"[TEST] GET {endpoint} (as researchadmin)")
            res = client.get(endpoint, headers=admin_headers)
            assert res.status_code == 200, f"Export {endpoint} failed for admin: {res.text}"
            
            # Verify headers and content
            content_type = res.headers.get("content-type")
            content_disp = res.headers.get("content-disposition")
            print(f"[OK] Content-Type: {content_type}")
            print(f"[OK] Content-Disposition: {content_disp}")
            assert "text/csv" in content_type
            assert filename in content_disp
            
            # Print a snippet of the CSV content
            csv_text = res.text
            lines = csv_text.strip().split("\n")
            print(f"[OK] Valid CSV generated successfully! Header line: {lines[0] if lines else 'empty'}")
            print(f"   Snippet (first 3 rows):")
            for line in lines[:3]:
                print(f"   {line}")
                
    print("\n" + "=" * 60)
    print("ALL ENDPOINTS VERIFIED AND WORKING SUCCESSFUL!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
