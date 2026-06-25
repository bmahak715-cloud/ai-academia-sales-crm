"""API integration tests for Academia Sales CRM."""
import requests

BASE = "http://localhost:5000/api"
session = requests.Session()


def test_login():
    r = session.post(f"{BASE}/auth/login", json={
        "email": "admin@academiacrm.com",
        "password": "admin123"
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    print("PASS: login")


def test_me():
    r = session.get(f"{BASE}/auth/me")
    assert r.status_code == 200
    print("PASS: me")


def test_institutions():
    r = session.get(f"{BASE}/institutions")
    assert r.status_code == 200
    data = r.json()
    assert len(data["institutions"]) > 0
    print(f"PASS: institutions ({len(data['institutions'])} leads)")


def test_dashboard():
    r = session.get(f"{BASE}/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "cards" in data
    print("PASS: dashboard")


def test_reports():
    r = session.get(f"{BASE}/reports")
    assert r.status_code == 200
    print("PASS: reports")


def test_follow_ups():
    r = session.get(f"{BASE}/follow-ups")
    assert r.status_code == 200
    print("PASS: follow-ups")


def test_meetings():
    r = session.get(f"{BASE}/meetings")
    assert r.status_code == 200
    print("PASS: meetings")


def test_notifications():
    r = session.get(f"{BASE}/notifications")
    assert r.status_code == 200
    print("PASS: notifications")


def test_create_lead():
    r = session.post(f"{BASE}/institutions", json={
        "name": "Test College API",
        "location": "Mumbai",
        "contact_person": "Test Person",
        "email": "test.api@college.edu.in",
        "phone": "9876543211",
        "institution_type": "Engineering College",
        "student_strength": 2000,
        "program_interest": "Data Science",
        "lead_source": "Website",
        "lead_status": "New Lead",
        "previous_partnership": False,
        "notes": "API test lead"
    })
    assert r.status_code == 201, f"Create failed: {r.text}"
    inst = r.json()["institution"]
    assert inst["ai_analysis"] is not None
    print(f"PASS: create lead (id={inst['id']}, ai_status={inst['ai_analysis']['status']})")
    return inst["id"]


def test_analyze_retry(lead_id):
    r = session.post(f"{BASE}/institutions/{lead_id}/analyze")
    assert r.status_code == 200
    print("PASS: analyze retry")


def test_delete_lead(lead_id):
    r = session.delete(f"{BASE}/institutions/{lead_id}")
    assert r.status_code == 200
    print("PASS: delete lead")


if __name__ == "__main__":
    test_login()
    test_me()
    test_institutions()
    test_dashboard()
    test_reports()
    test_follow_ups()
    test_meetings()
    test_notifications()
    lead_id = test_create_lead()
    test_analyze_retry(lead_id)
    test_delete_lead(lead_id)
    print("\nAll API tests passed!")
