from typing import Dict, Any
from copy import deepcopy
from db.repositories import save_resume_variant

def resume_positioning_node(state: Dict[str, Any]) -> Dict[str, Any]:

    resume = state["resume_artifact"]
    job = state["job_posting"]
    match = state["job_match"]

    candidate_id = state["candidate_profile"].get("_id", "default")

    job_skills = {s.lower() for s in job.get("skills", [])}
    resume_skills = resume.get("skills", [])

    # ---------- SKILL PRIORITIZATION ----------
    prioritized_skills = sorted(
        resume_skills,
        key=lambda s: s.lower() in job_skills,
        reverse=True
    )

    # ---------- PROJECT SELECTION (NO MUTATION) ----------
    relevant_projects = []
    for project in resume.get("projects", []):
        text = f"{project.get('title','')} {project.get('description','')}".lower()
        relevance = sum(1 for s in job_skills if s in text)

        if relevance > 0:
            p = deepcopy(project)
            p["relevance_score"] = relevance
            relevant_projects.append(p)

    relevant_projects.sort(
        key=lambda p: p["relevance_score"],
        reverse=True
    )

    top_projects = relevant_projects[:3]

    # ---------- HEADLINE ----------
    headline = job.get("title", "Machine Learning Engineer")

    # ---------- SUMMARY ----------
    summary = (
        f"AI/ML professional with strong experience in "
        f"{', '.join(match['evidence'].get('matched_skills', [])[:4])}. "
        f"Focused on building production-ready machine learning systems."
    )

    # ---------- KEYWORDS (ATS) ----------
    keywords = list(job_skills & {s.lower() for s in resume_skills})

    variant = {
        "headline": headline,
        "summary": summary,
        "skills": prioritized_skills,
        "projects": top_projects,
        "keywords": keywords
    }

    # ✅ PERSIST RESUME VARIANT
    save_resume_variant(job["job_id"], candidate_id, variant)

    return {"resume_variant": variant}
