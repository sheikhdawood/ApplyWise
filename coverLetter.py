from typing import Dict, Any
from db.repositories import save_cover_letter


def generate_with_llm(prompt: str) -> str:
    return "LLM_GENERATED_COVER_LETTER"


def cover_letter_node(state: Dict[str, Any]) -> Dict[str, Any]:

    decision = state["application_decision"]
    trust = state.get("platform_trust", {"automation_level": "LOW"})
    match = state["job_match"]
    job = state["job_posting"]

    resume = state.get("resume_variant") or state["resume_artifact"]
    candidate_id = state["candidate_profile"].get("_id", "default")

    # ---------- HARD NO COVER LETTER ----------
    if match["overall_score"] < 65:
        letter = {
            "text": None,
            "generated_by": "NONE",
            "confidence": 1.0,
            "reason": "Low match score"
        }
        save_cover_letter(job["job_id"], candidate_id, letter)
        return {"cover_letter": letter}

    if decision.get("requires_human") and trust.get("automation_level") != "FULL":
        letter = {
            "text": None,
            "generated_by": "NONE",
            "confidence": 1.0,
            "reason": "Human approval required"
        }
        save_cover_letter(job["job_id"], candidate_id, letter)
        return {"cover_letter": letter}

    if "no cover letter" in job.get("description", "").lower():
        letter = {
            "text": None,
            "generated_by": "NONE",
            "confidence": 1.0,
            "reason": "Job does not require cover letter"
        }
        save_cover_letter(job["job_id"], candidate_id, letter)
        return {"cover_letter": letter}

    # ---------- TEMPLATE LETTER ----------
    keywords = resume.get("keywords", resume.get("skills", []))

    template_letter = f"""
Dear Hiring Manager,

I am writing to express my interest in the {job.get('title')} position at {job.get('company')}.

My background includes hands-on experience with {', '.join(keywords[:5])},
and I have worked on projects that align closely with your requirements.

I am particularly interested in this role because it allows me to apply my skills
in building practical, production-focused AI/ML solutions.

Thank you for your time and consideration.

Sincerely,
""".strip()

    # ---------- LLM ENHANCEMENT ----------
    if trust.get("automation_level") == "FULL" and match["overall_score"] >= 75:

        prompt = f"""
STRICT RULES:
- Do NOT invent skills, companies, metrics, or experience
- Use ONLY provided info
- Max 300 words
- Professional tone

JOB:
{job}

RESUME:
{resume}
"""

        llm_text = generate_with_llm(prompt)

        letter = {
            "text": llm_text,
            "generated_by": "LLM",
            "confidence": round(match["overall_score"] / 100, 2)
        }

        save_cover_letter(job["job_id"], candidate_id, letter)
        return {"cover_letter": letter}

    # ---------- FALLBACK ----------
    letter = {
        "text": template_letter,
        "generated_by": "TEMPLATE",
        "confidence": 0.85
    }

    save_cover_letter(job["job_id"], candidate_id, letter)
    return {"cover_letter": letter}
