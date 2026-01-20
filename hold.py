from typing import Dict, Any
from db.repositories import save_hold

def hold_node(state: Dict[str, Any]) -> Dict[str, Any]:

    job = state["job_posting"]
    decision = state["application_decision"]
    quality = state.get("job_quality", {})
    match = state.get("job_match", {})

    candidate_id = state["candidate_profile"].get("candidate_id", "default")

    reasons = []

    if decision.get("reasoning"):
        reasons.extend(decision["reasoning"])

    if quality.get("verdict") == "REVIEW":
        reasons.append("Job quality requires review")

    if match.get("overall_score", 100) < 75:
        reasons.append("Match score not strong enough for auto-apply")

    hold_record = {
        "company": job.get("company"),
        "title": job.get("title"),
        "platform": job.get("platform"),
        "reason": reasons,
        "review_after_days": 7
    }

    # ✅ Persist HOLD
    save_hold(job["job_id"], candidate_id, hold_record)

    return {
        "hold_record": {
            "job_id": job["job_id"],
            **hold_record
        }
    }
