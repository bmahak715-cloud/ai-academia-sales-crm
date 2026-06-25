import os
import json
import re
from datetime import datetime
from app import db
from app.models.ai_analysis import AIAnalysis
from app.utils.validators import score_to_priority


def _fallback_analysis(institution):
    score = 40
    if institution.student_strength and institution.student_strength >= 5000:
        score += 20
    if institution.previous_partnership:
        score += 15
    if institution.institution_type in ("Private University", "Engineering College"):
        score += 10
    if institution.lead_source in ("Referral", "Existing Partner"):
        score += 10
    score = min(score, 100)
    priority = score_to_priority(score)
    return {
        "score": score,
        "priority": priority,
        "reason": f"Rule-based analysis: {institution.name} has {institution.student_strength} students, "
                  f"type {institution.institution_type}, source {institution.lead_source}.",
        "next_best_action": "Contact the institution within 24-48 hours to introduce training programs.",
        "outreach_message": (
            f"Dear {institution.contact_person},\n\n"
            f"We are pleased to connect with {institution.name} regarding our "
            f"{institution.program_interest} programs. We specialize in industry-aligned "
            f"technical training for academic institutions.\n\n"
            f"We would love to discuss how we can support your students and faculty.\n\n"
            f"Best regards,\nAcademia Sales Team"
        ),
        "follow_up_suggestions": [
            "Send program brochure via email",
            "Schedule a discovery call within 2 working days",
            "Connect on LinkedIn with the contact person"
        ]
    }


def _parse_ai_response(text):
    try:
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            data = json.loads(json_match.group())
            required = ["score", "priority", "reason", "next_best_action",
                        "outreach_message", "follow_up_suggestions"]
            if all(k in data for k in required):
                score = int(data["score"])
                score = max(0, min(100, score))
                priority = score_to_priority(score)
                suggestions = data["follow_up_suggestions"]
                if not isinstance(suggestions, list):
                    suggestions = [str(suggestions)]
                return {
                    "score": score,
                    "priority": priority,
                    "reason": str(data["reason"]),
                    "next_best_action": str(data["next_best_action"]),
                    "outreach_message": str(data["outreach_message"]),
                    "follow_up_suggestions": suggestions,
                }
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    return None


def analyze_lead(institution):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_anthropic_api_key_here":
        result = _fallback_analysis(institution)
        result["used_api"] = False
        return result, "Completed"

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Analyze this B2B academia sales lead and return ONLY valid JSON with no markdown:

Institution: {institution.name}
Location: {institution.location}
Contact: {institution.contact_person}
Type: {institution.institution_type}
Students: {institution.student_strength}
Program Interest: {institution.program_interest}
Lead Source: {institution.lead_source}
Status: {institution.lead_status}
Previous Partnership: {institution.previous_partnership}
Notes: {institution.notes or 'None'}

Return JSON:
{{
  "score": <0-100 integer>,
  "priority": "High|Medium|Low",
  "reason": "<brief reason>",
  "next_best_action": "<specific action>",
  "outreach_message": "<personalized email message>",
  "follow_up_suggestions": ["<suggestion1>", "<suggestion2>", "<suggestion3>"]
}}

Score mapping: 80-100 High, 50-79 Medium, 0-49 Low."""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text
        parsed = _parse_ai_response(text)
        if parsed:
            parsed["used_api"] = True
            return parsed, "Completed"
        result = _fallback_analysis(institution)
        result["used_api"] = False
        return result, "Completed"
    except Exception:
        return None, "Failed"


def save_analysis(institution, result, status):
    analysis = institution.ai_analysis
    if not analysis:
        analysis = AIAnalysis(institution_id=institution.id)
        db.session.add(analysis)

    if result and status == "Completed":
        analysis.score = result["score"]
        analysis.priority = result["priority"]
        analysis.reason = result["reason"]
        analysis.next_best_action = result["next_best_action"]
        analysis.outreach_message = result["outreach_message"]
        analysis.follow_up_suggestions = json.dumps(result["follow_up_suggestions"])
        analysis.status = "Completed"
        analysis.analyzed_at = datetime.utcnow()
    else:
        analysis.status = "Failed"
        analysis.analyzed_at = datetime.utcnow()

    db.session.commit()
    return analysis


def regenerate_outreach(institution):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_anthropic_api_key_here":
        result = _fallback_analysis(institution)
        return result["outreach_message"], True

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Write a professional outreach email for:
Institution: {institution.name}
Contact: {institution.contact_person}
Program: {institution.program_interest}
Type: {institution.institution_type}

Return only the email body text, no subject line."""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip(), True
    except Exception:
        result = _fallback_analysis(institution)
        return result["outreach_message"], False


def generate_follow_up_message(institution, context=""):
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    fallback = (
        f"Dear {institution.contact_person},\n\n"
        f"Following up on our previous conversation about {institution.program_interest} "
        f"programs at {institution.name}. I wanted to check if you had any questions "
        f"or would like to schedule a brief call.\n\n"
        f"Best regards,\nAcademia Sales Team"
    )
    if not api_key or api_key == "your_anthropic_api_key_here":
        return fallback

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Write a follow-up email for:
Institution: {institution.name}
Contact: {institution.contact_person}
Program: {institution.program_interest}
Context: {context or 'General follow-up'}
Return only the email body."""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip(), True
    except Exception:
        return fallback
