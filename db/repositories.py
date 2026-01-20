from db.client import db
from datetime import datetime

def save_job(job: dict) -> bool:
    """
    Saves a job if it does not already exist.
    Returns True if inserted, False if already existed.
    """
    result = db.jobs.update_one(
        {"_id": job["job_id"]},
        {
            "$setOnInsert": {
                **job,
                "status": "ACTIVE",
                "discovered_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    # If upserted_id is not None → new job
    return result.upserted_id is not None

def save_job_quality(job_id: str, quality: dict):
    doc = quality.copy()
    doc["job_id"] = job_id
    doc["evaluated_at"] = datetime.utcnow()

    db.job_quality.update_one(
        {"job_id": job_id},
        {"$set": doc},
        upsert=True
    )

def save_decision(job_id: str, candidate_id: str, decision: dict):
    """
    Persist application decision.
    One decision per job per candidate.
    """
    doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        **decision,
        "decided_at": datetime.utcnow()
    }

    db.decisions.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": doc},
        upsert=True
    )

def save_hold(job_id: str, candidate_id: str, hold: dict):
    """
    Persist HOLD decision for later review.
    """
    doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        **hold,
        "held_at": datetime.utcnow()
    }

    db.holds.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": doc},
        upsert=True
    )

def save_archive(job_id: str, candidate_id: str, archive: dict):
    """
    Permanently archive a job (never reconsider).
    """
    doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        **archive,
        "archived_at": datetime.utcnow()
    }

    db.archives.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": doc},
        upsert=True
    )

def save_application(job_id: str, candidate_id: str, application: dict):
    """
    Persist job application attempt.
    One application per job per candidate.
    """
    doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        **application,
        "applied_at": datetime.utcnow()
    }

    db.applications.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": doc},
        upsert=True
    )

def save_trust_state(platform: str, trust: dict):
    """
    Persist platform trust state.
    One document per platform.
    """
    doc = {
        "platform": platform,
        **trust,
        "updated_at": datetime.utcnow()
    }

    db.trust_state.update_one(
        {"platform": platform},
        {"$set": doc},
        upsert=True
    )

def save_candidate(candidate_id: str, candidate: dict):
    db.candidates.update_one(
        {"_id": candidate_id},
        {"$set": candidate},
        upsert=True
    )

def save_resume(resume_hash: str, resume: dict):
    db.resumes.update_one(
        {"_id": resume_hash},
        {"$set": resume},
        upsert=True
    )

def save_job_match(job_id: str, candidate_id: str, match: dict):
    doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        **match,
        "matched_at": datetime.utcnow()
    }

    db.job_matches.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": doc},
        upsert=True
    )

def save_resume_variant(job_id: str, candidate_id: str, variant: dict):
    doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        **variant,
        "created_at": datetime.utcnow()
    }

    db.resume_variants.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": doc},
        upsert=True
    )

def save_cover_letter(job_id: str, candidate_id: str, letter: dict):
    doc = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        **letter,
        "created_at": datetime.utcnow()
    }

    db.cover_letters.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": doc},
        upsert=True
    )

def has_application(job_id: str, candidate_id: str) -> bool:
    return db.applications.find_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"_id": 1}
    ) is not None


def is_archived(job_id: str, candidate_id: str) -> bool:
    return db.archives.find_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"_id": 1}
    ) is not None


def has_skip_decision(job_id: str, candidate_id: str) -> bool:
    doc = db.decisions.find_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"action": 1}
    )
    return doc is not None and doc.get("action") == "SKIP"


def is_on_hold(job_id: str, candidate_id: str) -> bool:
    return db.holds.find_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"_id": 1}
    ) is not None
