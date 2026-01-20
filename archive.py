from typing import Dict, Any
from db.repositories import save_archive

def archive_node(state: Dict[str, Any]) -> Dict[str, Any]:

    job = state.get("job_posting", {})
    decision = state.get("application_decision", {})
    quality = state.get("job_quality", {})
    match = state.get("job_match", {})

    candidate_id = state["candidate_profile"].get("candidate_id", "default")

    reasons = []

    # Explicit decision reasoning
    if decision.get("reasoning"):
        reasons.extend(decision["reasoning"])

    # Quality failure
    if quality.get("verdict") == "FAIL":
        reasons.append("Failed job quality checks")

    # Low match
    if match.get("overall_score", 100) < 45:
        reasons.append("Very low resume-job match")

    # Platform safety issues
    error = (
        state.get("application_result", {})
        .get("error", "")
        .lower()
    )
    if "captcha" in error:
        reasons.append("CAPTCHA detected — platform risk")
    if "login" in error:
        reasons.append("Login wall detected")
    if "warning" in error:
        reasons.append("Platform warning detected")

    if not reasons:
        reasons.append("Archived by system policy")

    archive_record = {
        "company": job.get("company"),
        "title": job.get("title"),
        "platform": job.get("platform"),
        "reason": reasons
    }

    # ✅ Persist ARCHIVE
    save_archive(job.get("job_id"), candidate_id, archive_record)

    return {
        "archive_record": {
            "job_id": job.get("job_id"),
            **archive_record
        }
    }
