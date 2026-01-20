import requests
import hashlib
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from datetime import datetime
from db.repositories import save_job

AIML_ROLE_KEYWORDS = {
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
    "data scientist",
    "applied scientist",
    "genai",
    "llm"
}

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def job_fingerprint(title: str, company: str, location: str) -> str:
    key = f"{normalize(title)}|{normalize(company)}|{normalize(location)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def is_aiml_role(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in AIML_ROLE_KEYWORDS)

def fetch_company_jobs(url: str, platform_name="COMPANY") -> List[Dict[str, Any]]:
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        link = a.get("href")

        if not title or not link:
            continue

        if not is_aiml_role(title):
            continue

        jobs.append({
            "title": title,
            "company": url.split("//")[-1].split("/")[0],
            "location": "Unknown",
            "platform": platform_name,
            "job_url": link if link.startswith("http") else url + link,
            "description": "",     # fetched later if needed
            "skills": [],
            "posted_days_ago": 0
        })

    return jobs

def discover_jobs(candidate_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    discovered = []

    # Example company career pages (expand later)
    company_pages = [
        "https://boards.greenhouse.io/databricks",
        "https://boards.greenhouse.io/openai",
        "https://boards.greenhouse.io/anthropic",
        "https://jobs.lever.co/huggingface",
        "https://jobs.lever.co/scaleai",
        "https://boards.greenhouse.io/stripe",
    ]


    for page in company_pages:
        try:
            jobs = fetch_company_jobs(page)
            discovered.extend(jobs)
        except Exception:
            continue

    return discovered

def job_discovery_node(state: Dict[str, Any]) -> Dict[str, Any]:

    candidate = state["candidate_profile"]
    jobs = discover_jobs(candidate)

    if not jobs:
        raise RuntimeError("No jobs discovered")

    for raw_job in jobs:

        job_id = job_fingerprint(
            raw_job["title"],
            raw_job["company"],
            raw_job["location"]
        )

        job = {
            "job_id": job_id,
            "title": raw_job["title"],
            "company": raw_job["company"],
            "location": raw_job["location"],
            "platform": raw_job["platform"],
            "job_url": raw_job["job_url"],
            "description": raw_job.get("description", ""),
            "skills": raw_job.get("skills", []),
            "posted_days_ago": raw_job.get("posted_days_ago", 0),
            "discovered_at": datetime.utcnow()
        }

        # ✅ PERSIST JOB (SIDE EFFECT)
        is_new = save_job(job)

        # ✅ ONLY RETURN NEW JOBS INTO GRAPH
        if is_new:
            return {
                "job_posting": job,
                "timestamps": {
                    "job_discovered": datetime.utcnow()
                }
            }

    # If we reach here → all discovered jobs already exist
    raise RuntimeError("No new jobs discovered")
