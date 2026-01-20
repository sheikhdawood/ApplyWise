from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["job_agent_db"]

# ---------- READ HELPERS ----------

def get_jobs(limit=100):
    return list(db.jobs.find().sort("discovered_at", -1).limit(limit))

def get_decisions():
    return list(db.decisions.find().sort("decided_at", -1))

def get_holds():
    return list(db.holds.find().sort("held_at", -1))

def get_archives():
    return list(db.archives.find().sort("archived_at", -1))

def get_applications():
    return list(db.applications.find().sort("applied_at", -1))

def get_trust_states():
    return list(db.trust_state.find())

def get_job_quality(job_id):
    return db.job_quality.find_one({"job_id": job_id})

def get_job_match(job_id, candidate_id):
    return db.job_matches.find_one({
        "job_id": job_id,
        "candidate_id": candidate_id
    })
