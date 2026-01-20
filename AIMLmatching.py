import re
from typing import Dict, Any, Set
from db.repositories import save_job_match


def normalize_skills(skills: list[str]) -> Set[str]:
    return {s.lower().strip() for s in skills}


def infer_required_years(text: str) -> int | None:
    match = re.search(r"(\d+)\+?\s*years", text.lower())
    return int(match.group(1)) if match else None


def aiml_matching_node(state: Dict[str, Any]) -> Dict[str, Any]:

    candidate = state["candidate_profile"]
    resume = state["resume_artifact"]
    job = state["job_posting"]

    candidate_id = candidate.get("_id", "default")

    # ---------- NORMALIZATION ----------
    candidate_skills = normalize_skills(
        candidate.get("skills", []) +
        resume.get("skills", []) +
        resume.get("tools", [])  # safe now
    )

    job_skills = normalize_skills(job.get("skills", []))

    # ---------- SKILL MATCH ----------
    matched_skills = candidate_skills & job_skills
    missing_skills = list(job_skills - candidate_skills)

    if job_skills:
        skill_score = (len(matched_skills) / len(job_skills)) * 100
    else:
        skill_score = 50

    # ---------- DOMAIN MATCH ----------
    domains = {d.lower() for d in candidate.get("primary_domains", [])}
    job_text = job.get("description", "").lower()

    domain_hits = sum(1 for d in domains if d in job_text)
    domain_score = min(100, domain_hits * 40)

    # ---------- SENIORITY MATCH ----------
    required_years = infer_required_years(job.get("experience_required", ""))

    if required_years is None:
        seniority_score = 70
    else:
        diff = candidate.get("years_experience", 0) - required_years
        if diff >= 0:
            seniority_score = 100
        elif diff >= -1:
            seniority_score = 70
        else:
            seniority_score = 30

    # ---------- FINAL SCORE ----------
    overall_score = (
        skill_score * 0.45 +
        domain_score * 0.30 +
        seniority_score * 0.25
    )

    match = {
        "overall_score": round(overall_score, 2),
        "skill_match": round(skill_score, 2),
        "domain_match": round(domain_score, 2),
        "seniority_match": round(seniority_score, 2),
        "missing_skills": missing_skills,
        "evidence": {
            "matched_skills": list(matched_skills),
            "required_years": required_years,
            "candidate_years": candidate.get("years_experience")
        }
    }

    # ✅ PERSIST MATCH RESULT
    save_job_match(job["job_id"], candidate_id, match)

    return {"job_match": match}
