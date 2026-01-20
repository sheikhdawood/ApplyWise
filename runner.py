from main import application_graph
from preFilter import should_run_graph
from jobDiscovery import discover_jobs, job_fingerprint
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def run_batch():
    candidate_profile = {
        "_id": "default",
        "skills": ["python", "llm"],
        "years_experience": 4,
        "primary_domains": ["ai", "ml"]
    }

    raw_jobs = discover_jobs(candidate_profile)

    logging.info(f"🔍 Discovered {len(raw_jobs)} jobs")

    for raw_job in raw_jobs:

        job_id = job_fingerprint(
            raw_job["title"],
            raw_job["company"],
            raw_job["location"]
        )

        job = {
            "job_id": job_id,
            **raw_job
        }

        allowed, reason = should_run_graph(job_id, candidate_profile["_id"])
        if not allowed:
            logging.info(f"⏭️ Skipping job {job_id}: {reason}")
            continue

        logging.info(f"▶️ Running agent for {job['title']}")

        application_graph.invoke({
            "job_posting": job,
            "candidate_profile": candidate_profile,
            "resume_path": "resumes/sir.pdf",
            "platform_trust": {},
            "kill_switch": False
        })

        logging.info(f"✅ Finished {job['title']}")

if __name__ == "__main__":
    logging.info("🚀 AutoApply Agent Started")
    run_batch()
