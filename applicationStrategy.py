from typing import Dict, Any
from db.repositories import save_decision

QUALITY_MIN_SCORE = 70
MATCH_MIN_SCORE = 72
SKILL_MIN_SCORE = 65
SENIORITY_MIN_SCORE = 60


def application_strategy_node(state: Dict[str, Any]) -> Dict[str, Any]:

    job = state["job_posting"]
    quality = state["job_quality"]
    match = state["job_match"]

    candidate_id = state["candidate_profile"].get("candidate_id", "default")
    trust = state.get("platform_trust", {"automation_level": "LIMITED"})

    reasoning = []

    # ---------- HARD SKIP ----------
    if quality["verdict"] == "FAIL":
        decision = {
            "action": "SKIP",
            "confidence": 1.0,
            "requires_human": False,
            "reasoning": ["Failed job quality checks"]
        }
        save_decision(job["job_id"], candidate_id, decision)
        return {"application_decision": decision}

    if match["overall_score"] < 45:
        decision = {
            "action": "SKIP",
            "confidence": 1.0,
            "requires_human": False,
            "reasoning": ["Very low resume-job match"]
        }
        save_decision(job["job_id"], candidate_id, decision)
        return {"application_decision": decision}

    # ---------- APPLY ----------
    if (
        quality["score"] >= QUALITY_MIN_SCORE and
        match["overall_score"] >= MATCH_MIN_SCORE and
        match["skill_match"] >= SKILL_MIN_SCORE and
        match["seniority_match"] >= SENIORITY_MIN_SCORE
    ):
        reasoning.extend([
            "High job quality",
            "Strong AIML alignment",
            "Acceptable seniority match"
        ])

        decision = {
            "action": "APPLY",
            "confidence": round(match["overall_score"] / 100, 2),
            "requires_human": trust.get("automation_level") != "FULL",
            "reasoning": reasoning
        }

        save_decision(job["job_id"], candidate_id, decision)
        return {"application_decision": decision}

    # ---------- HOLD ----------
    reasoning.append("Partial match or automation not trusted yet")

    if match.get("missing_skills"):
        reasoning.append(f"Missing skills: {match['missing_skills'][:3]}")

    decision = {
        "action": "HOLD",
        "confidence": round(match["overall_score"] / 100, 2),
        "requires_human": True,
        "reasoning": reasoning
    }

    save_decision(job["job_id"], candidate_id, decision)
    return {"application_decision": decision}
