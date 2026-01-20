import re
from typing import Dict, Any
from db.repositories import save_job_quality

AIML_KEYWORDS = {
    "machine learning", "deep learning", "artificial intelligence",
    "nlp", "computer vision", "llm", "genai", "data science",
    "pytorch", "tensorflow", "transformers"
}

SCAM_KEYWORDS = {
    "quick money", "whatsapp", "telegram", "pay to apply",
    "registration fee", "training fee"
}

QUALITY_PASS_THRESHOLD = 55


def job_quality_filter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state["job_posting"]

    reasons = []
    risk_flags = []
    score = 0.0

    text_blob = f"{job.get('title','')} {job.get('description','')}".lower()

    # ---------- HARD FAIL RULES ----------
    if any(k in text_blob for k in SCAM_KEYWORDS):
        quality = {
            "score": 0,
            "verdict": "FAIL",
            "reasons": ["Scam indicators detected"],
            "risk_flags": ["SCAM"]
        }
        save_job_quality(job["job_id"], quality)
        return {"job_quality": quality}

    if "intern" in text_blob or "fresher" in text_blob:
        quality = {
            "score": 0,
            "verdict": "FAIL",
            "reasons": ["Internship/Fresher role"],
            "risk_flags": ["ROLE_MISMATCH"]
        }
        save_job_quality(job["job_id"], quality)
        return {"job_quality": quality}

    if not job.get("company"):
        quality = {
            "score": 0,
            "verdict": "FAIL",
            "reasons": ["Missing company name"],
            "risk_flags": ["LOW_CREDIBILITY"]
        }
        save_job_quality(job["job_id"], quality)
        return {"job_quality": quality}

    # ---------- SCORING ----------
    # AIML relevance
    aiml_hits = sum(1 for k in AIML_KEYWORDS if k in text_blob)
    score += min(30, aiml_hits * 6)

    if aiml_hits == 0:
        reasons.append("Weak AIML relevance")

    # Skills clarity
    skills = job.get("skills", [])
    if len(skills) >= 6:
        score += 20
    elif len(skills) >= 3:
        score += 12
    else:
        reasons.append("Low skill specificity")

    # Experience alignment
    exp_text = job.get("experience_required", "").lower()
    if re.search(r"\b(3|4|5)\+?\s*years\b", exp_text):
        score += 15
    elif exp_text:
        score += 8
    else:
        reasons.append("Unclear experience requirement")

    # Job freshness
    days = job.get("posted_days_ago", 30)
    if days <= 7:
        score += 15
    elif days <= 14:
        score += 8
    else:
        reasons.append("Old job posting")

    # Compensation transparency
    if job.get("salary_range"):
        score += 10
    else:
        reasons.append("No salary info")

    # Company legitimacy
    if len(job.get("company", "")) > 2:
        score += 10

    verdict = "PASS" if score >= QUALITY_PASS_THRESHOLD else "FAIL"
    if verdict == "FAIL":
        risk_flags.append("LOW_QUALITY")

    quality = {
        "score": round(score, 2),
        "verdict": verdict,
        "reasons": reasons,
        "risk_flags": risk_flags
    }

    # ✅ Persist ONCE
    save_job_quality(job["job_id"], quality)

    return {"job_quality": quality}
