from datetime import datetime, date, timedelta
import json
from app import db
from app.models.user import User
from app.models.institution import Institution
from app.models.ai_analysis import AIAnalysis
from app.models.follow_up import FollowUp
from app.models.meeting import Meeting
from app.models.activity import Activity
from app.models.notification import Notification
from app.models.communication import Communication


def seed_if_empty():
    if User.query.first():
        return

    users_data = [
        {"name": "Admin User", "email": "admin@academiacrm.com", "password": "admin123",
         "role": "Admin", "region": "National"},
        {"name": "Rajesh Kumar", "email": "rajesh@academiacrm.com", "password": "sales123",
         "role": "Sales Manager", "region": "North India"},
        {"name": "Priya Sharma", "email": "priya@academiacrm.com", "password": "sales123",
         "role": "Sales Executive", "region": "North India"},
        {"name": "Amit Patel", "email": "amit@academiacrm.com", "password": "sales123",
         "role": "Sales Executive", "region": "West India"},
        {"name": "Sneha Reddy", "email": "sneha@academiacrm.com", "password": "sales123",
         "role": "Sales Executive", "region": "South India"},
    ]

    users = {}
    for u in users_data:
        user = User(
            name=u["name"], email=u["email"], role=u["role"],
            region=u["region"], is_active=True
        )
        user.set_password(u["password"])
        db.session.add(user)
        users[u["email"]] = user
    db.session.commit()

    institutions_data = [
        {
            "name": "GLA University", "location": "Mathura, UP",
            "contact_person": "Dr. Anil Verma", "email": "anil.verma@gla.edu.in",
            "phone": "9876543210", "institution_type": "Private University",
            "student_strength": 8000, "program_interest": "Artificial Intelligence",
            "lead_source": "Education Conference", "lead_status": "Meeting Scheduled",
            "assigned_to": "priya@academiacrm.com", "previous_partnership": True,
            "notes": "Interested in AI lab setup and faculty training.",
            "ai_score": 88, "ai_priority": "High",
        },
        {
            "name": "ABC Engineering College", "location": "Pune, Maharashtra",
            "contact_person": "Prof. Meera Joshi", "email": "meera@abceng.edu.in",
            "phone": "9123456780", "institution_type": "Engineering College",
            "student_strength": 3500, "program_interest": "Data Science",
            "lead_source": "LinkedIn", "lead_status": "Contacted",
            "assigned_to": "amit@academiacrm.com", "previous_partnership": False,
            "notes": "Looking for placement training programs.",
            "ai_score": 62, "ai_priority": "Medium",
        },
        {
            "name": "Delhi Technical Institute", "location": "New Delhi",
            "contact_person": "Mr. Vikram Singh", "email": "vikram@dti.edu.in",
            "phone": "9988776655", "institution_type": "Training Institute",
            "student_strength": 1200, "program_interest": "Web Development",
            "lead_source": "Website", "lead_status": "New Lead",
            "assigned_to": "priya@academiacrm.com", "previous_partnership": False,
            "notes": "Submitted inquiry through website contact form.",
            "ai_score": 45, "ai_priority": "Low",
        },
        {
            "name": "Jaipur Business School", "location": "Jaipur, Rajasthan",
            "contact_person": "Dr. Kavita Rathore", "email": "kavita@jbs.edu.in",
            "phone": "9876512340", "institution_type": "Management College",
            "student_strength": 2500, "program_interest": "Cloud Computing",
            "lead_source": "Referral", "lead_status": "Proposal Sent",
            "assigned_to": "amit@academiacrm.com", "previous_partnership": True,
            "notes": "Referred by existing partner. Budget discussion ongoing.",
            "ai_score": 75, "ai_priority": "Medium",
        },
        {
            "name": "North India University", "location": "Chandigarh",
            "contact_person": "Prof. Harish Malhotra", "email": "harish@niu.edu.in",
            "phone": "9012345678", "institution_type": "Government University",
            "student_strength": 12000, "program_interest": "Machine Learning",
            "lead_source": "Existing Partner", "lead_status": "Negotiation",
            "assigned_to": "sneha@academiacrm.com", "previous_partnership": True,
            "notes": "Large university, multi-year partnership potential.",
            "ai_score": 92, "ai_priority": "High",
        },
        {
            "name": "South Point College", "location": "Kolkata, West Bengal",
            "contact_person": "Ms. Ritu Banerjee", "email": "ritu@southpoint.edu.in",
            "phone": "9876501234", "institution_type": "Degree College",
            "student_strength": 1800, "program_interest": "Cybersecurity",
            "lead_source": "Email Campaign", "lead_status": "Closed-Won",
            "assigned_to": "sneha@academiacrm.com", "previous_partnership": False,
            "notes": "Signed contract for cybersecurity workshop series.",
            "ai_score": 70, "ai_priority": "Medium",
        },
        {
            "name": "Tech Valley Institute", "location": "Hyderabad, Telangana",
            "contact_person": "Dr. Srinivas Rao", "email": "srinivas@techvalley.edu.in",
            "phone": "9123409876", "institution_type": "Training Institute",
            "lead_source": "Manual Research", "lead_status": "Closed-Lost",
            "assigned_to": "priya@academiacrm.com", "previous_partnership": False,
            "student_strength": 800, "program_interest": "Placement Training",
            "notes": "Budget constraints, may revisit next quarter.",
            "ai_score": 35, "ai_priority": "Low",
        },
    ]

    inst_map = {}
    for d in institutions_data:
        inst = Institution(
            name=d["name"], location=d["location"],
            contact_person=d["contact_person"], email=d["email"],
            phone=d["phone"], institution_type=d["institution_type"],
            student_strength=d["student_strength"],
            program_interest=d["program_interest"],
            lead_source=d["lead_source"], lead_status=d["lead_status"],
            assigned_to_id=users[d["assigned_to"]].id,
            previous_partnership=d["previous_partnership"],
            notes=d["notes"],
            created_at=datetime.utcnow() - timedelta(days=30),
        )
        db.session.add(inst)
        db.session.flush()

        analysis = AIAnalysis(
            institution_id=inst.id,
            score=d["ai_score"],
            priority=d["ai_priority"],
            reason=f"Demo analysis for {d['name']}: {d['student_strength']} students, "
                   f"{d['institution_type']}, source {d['lead_source']}.",
            next_best_action="Follow up with contact person within 48 hours.",
            outreach_message=f"Dear {d['contact_person']},\n\nWe are excited to partner with "
                             f"{d['name']} for {d['program_interest']} programs.\n\nBest regards",
            follow_up_suggestions=json.dumps([
                "Send program brochure", "Schedule discovery call", "Share case studies"
            ]),
            status="Completed",
            analyzed_at=datetime.utcnow(),
        )
        db.session.add(analysis)
        inst_map[d["name"]] = inst

    db.session.commit()

    today = date.today()
    follow_ups_data = [
        ("GLA University", "Initial contact call", "Phone Call", today, "High", "Pending", "priya@academiacrm.com"),
        ("ABC Engineering College", "Send data science brochure", "Send Brochure", today + timedelta(days=1), "Medium", "Pending", "amit@academiacrm.com"),
        ("Delhi Technical Institute", "Welcome email follow-up", "Email Follow-up", today - timedelta(days=2), "High", "Pending", "priya@academiacrm.com"),
        ("Jaipur Business School", "Proposal follow-up call", "Proposal Follow-up", today + timedelta(days=3), "High", "Pending", "amit@academiacrm.com"),
        ("North India University", "Negotiation meeting prep", "Negotiation Follow-up", today, "High", "Pending", "sneha@academiacrm.com"),
        ("South Point College", "Onboarding kickoff", "General Follow-up", today - timedelta(days=5), "Low", "Completed", "sneha@academiacrm.com"),
    ]

    for name, title, task_type, due, priority, status, assignee in follow_ups_data:
        fu = FollowUp(
            institution_id=inst_map[name].id,
            title=title, task_type=task_type,
            description=f"Task for {name}",
            due_date=due, priority=priority,
            assigned_to_id=users[assignee].id,
            status=status,
            completed_at=datetime.utcnow() if status == "Completed" else None,
        )
        db.session.add(fu)

    meetings_data = [
        ("GLA University", "Dr. Anil Verma", today + timedelta(days=2), "10:00 AM",
         "Online", "https://meet.google.com/demo-gla", "AI program discussion", "Scheduled", "priya@academiacrm.com"),
        ("Jaipur Business School", "Dr. Kavita Rathore", today + timedelta(days=5), "2:00 PM",
         "Offline", "Jaipur Business School, Conference Room", "Cloud computing proposal review", "Scheduled", "amit@academiacrm.com"),
        ("North India University", "Prof. Harish Malhotra", today - timedelta(days=3), "11:00 AM",
         "Online", "https://meet.google.com/demo-niu", "ML partnership negotiation", "Completed", "sneha@academiacrm.com"),
    ]

    for name, contact, mdate, mtime, mode, loc, agenda, status, assignee in meetings_data:
        m = Meeting(
            institution_id=inst_map[name].id,
            contact_person=contact,
            meeting_date=mdate, meeting_time=mtime,
            mode=mode, location_or_link=loc,
            agenda=agenda, status=status,
            assigned_to_id=users[assignee].id,
            meeting_notes="Demo meeting notes" if status == "Completed" else None,
            requirements="Lab setup, faculty training" if status == "Completed" else None,
            budget_discussion="₹15L annual" if status == "Completed" else None,
        )
        db.session.add(m)

    for name, inst in inst_map.items():
        act = Activity(
            institution_id=inst.id,
            activity_type="Lead created",
            description=f"Lead {name} was added to the system.",
            user_id=users["admin@academiacrm.com"].id,
            created_at=datetime.utcnow() - timedelta(days=25),
        )
        db.session.add(act)

    for email, user in users.items():
        n = Notification(
            user_id=user.id,
            notification_type="System",
            message="Welcome to Academia Sales CRM! Demo data has been loaded.",
            is_read=False,
        )
        db.session.add(n)

    comm = Communication(
        institution_id=inst_map["GLA University"].id,
        message_type="outreach",
        subject="AI Training Partnership",
        body="Dear Dr. Anil Verma,\n\nWe are pleased to connect regarding AI programs at GLA University.",
        status="Sent",
        sent_at=datetime.utcnow() - timedelta(days=5),
        created_by_id=users["priya@academiacrm.com"].id,
    )
    db.session.add(comm)

    db.session.commit()
