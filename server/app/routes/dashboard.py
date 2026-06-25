from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify
from sqlalchemy import func, extract
from app import db
from app.models.institution import Institution
from app.models.ai_analysis import AIAnalysis
from app.models.follow_up import FollowUp
from app.models.meeting import Meeting
from app.models.activity import Activity
from app.utils.auth import login_required
from app.utils.validators import LEAD_STATUSES

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
@login_required
def get_dashboard():
    today = date.today()
    total_leads = Institution.query.count()
    active_statuses = ["New Lead", "Contacted", "Meeting Scheduled", "Proposal Sent", "Negotiation"]
    active_leads = Institution.query.filter(Institution.lead_status.in_(active_statuses)).count()
    contacted = Institution.query.filter(Institution.lead_status != "New Lead").count()
    meetings_scheduled = Meeting.query.filter_by(status="Scheduled").count()
    closed_won = Institution.query.filter_by(lead_status="Closed-Won").count()
    closed_lost = Institution.query.filter_by(lead_status="Closed-Lost").count()
    new_leads = Institution.query.filter_by(lead_status="New Lead").count()

    high_priority = db.session.query(Institution).join(AIAnalysis).filter(
        AIAnalysis.priority == "High"
    ).count()

    follow_ups_today = FollowUp.query.filter(
        FollowUp.status != "Completed",
        FollowUp.due_date == today
    ).count()

    overdue_follow_ups = FollowUp.query.filter(
        FollowUp.status != "Completed",
        FollowUp.due_date < today
    ).count()

    conversion_rate = round((closed_won / total_leads * 100) if total_leads > 0 else 0, 1)

    pipeline = []
    for status in LEAD_STATUSES:
        count = Institution.query.filter_by(lead_status=status).count()
        pipeline.append({"status": status, "count": count})

    upcoming_meetings = Meeting.query.filter(
        Meeting.status == "Scheduled",
        Meeting.meeting_date >= today
    ).order_by(Meeting.meeting_date).limit(5).all()

    due_today_tasks = FollowUp.query.filter(
        FollowUp.status != "Completed",
        FollowUp.due_date == today
    ).limit(5).all()

    high_priority_leads = db.session.query(Institution).join(AIAnalysis).filter(
        AIAnalysis.priority == "High"
    ).order_by(AIAnalysis.score.desc()).limit(5).all()

    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(10).all()

    top_insight = db.session.query(Institution).join(AIAnalysis).filter(
        AIAnalysis.status == "Completed"
    ).order_by(AIAnalysis.score.desc()).first()

    insight_data = None
    if top_insight and top_insight.ai_analysis:
        insight_data = {
            "institution_name": top_insight.name,
            "score": top_insight.ai_analysis.score,
            "priority": top_insight.ai_analysis.priority,
            "reason": top_insight.ai_analysis.reason,
            "next_best_action": top_insight.ai_analysis.next_best_action,
        }

    return jsonify({
        "cards": {
            "total_institutions_contacted": contacted,
            "active_leads": active_leads,
            "meetings_scheduled": meetings_scheduled,
            "conversion_status": f"{conversion_rate}%",
        },
        "stats": {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "high_priority_leads": high_priority,
            "follow_ups_due_today": follow_ups_today,
            "overdue_follow_ups": overdue_follow_ups,
            "closed_won": closed_won,
            "closed_lost": closed_lost,
            "conversion_rate": conversion_rate,
        },
        "pipeline": pipeline,
        "upcoming_meetings": [m.to_dict() for m in upcoming_meetings],
        "follow_ups_due_today": [f.to_dict() for f in due_today_tasks],
        "high_priority_leads": [i.to_dict() for i in high_priority_leads],
        "recent_activities": [a.to_dict() for a in recent_activities],
        "top_ai_insight": insight_data,
    })


@dashboard_bp.route("/reports", methods=["GET"])
@login_required
def get_reports():
    total_leads = Institution.query.count()
    closed_won = Institution.query.filter_by(lead_status="Closed-Won").count()
    closed_lost = Institution.query.filter_by(lead_status="Closed-Lost").count()
    conversion_rate = round((closed_won / total_leads * 100) if total_leads > 0 else 0, 1)

    leads_by_status = []
    for status in LEAD_STATUSES:
        count = Institution.query.filter_by(lead_status=status).count()
        leads_by_status.append({"name": status, "value": count})

    leads_by_priority = []
    for priority in ["High", "Medium", "Low"]:
        count = db.session.query(Institution).join(AIAnalysis).filter(
            AIAnalysis.priority == priority
        ).count()
        leads_by_priority.append({"name": priority, "value": count})

    leads_by_source = db.session.query(
        Institution.lead_source, func.count(Institution.id)
    ).group_by(Institution.lead_source).all()
    leads_by_source = [{"name": s, "value": c} for s, c in leads_by_source]

    leads_by_type = db.session.query(
        Institution.institution_type, func.count(Institution.id)
    ).group_by(Institution.institution_type).all()
    leads_by_type = [{"name": t, "value": c} for t, c in leads_by_type]

    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly = db.session.query(
        extract("year", Institution.created_at).label("year"),
        extract("month", Institution.created_at).label("month"),
        func.count(Institution.id)
    ).filter(Institution.created_at >= six_months_ago).group_by(
        "year", "month"
    ).order_by("year", "month").all()

    monthly_leads = [
        {"name": f"{int(m.year)}-{int(m.month):02d}", "value": m[2]}
        for m in monthly
    ]

    meetings_scheduled = Meeting.query.filter_by(status="Scheduled").count()
    meetings_completed = Meeting.query.filter_by(status="Completed").count()
    meetings_cancelled = Meeting.query.filter_by(status="Cancelled").count()

    pipeline = []
    for status in LEAD_STATUSES:
        count = Institution.query.filter_by(lead_status=status).count()
        pipeline.append({"status": status, "count": count})

    return jsonify({
        "leads_by_status": leads_by_status,
        "leads_by_priority": leads_by_priority,
        "leads_by_source": leads_by_source,
        "leads_by_type": leads_by_type,
        "monthly_leads": monthly_leads,
        "meetings": {
            "scheduled": meetings_scheduled,
            "completed": meetings_completed,
            "cancelled": meetings_cancelled,
        },
        "closed_won_vs_lost": [
            {"name": "Closed-Won", "value": closed_won},
            {"name": "Closed-Lost", "value": closed_lost},
        ],
        "conversion_rate": conversion_rate,
        "pipeline": pipeline,
        "total_leads": total_leads,
    })
