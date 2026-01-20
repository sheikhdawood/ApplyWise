import os
import re
import hashlib
from typing import Dict, Any, List
from db.repositories import save_candidate, save_resume
from datetime import datetime

import pdfplumber
from docx import Document

# Minimal, expandable AIML skill dictionary
AIML_SKILLS = {
    "python", "machine learning", "deep learning", "nlp",
    "computer vision", "llm", "genai", "rag",
    "pytorch", "tensorflow", "scikit-learn",
    "fastapi", "docker", "kubernetes",
    "langchain", "transformers", "huggingface",
    "aws", "gcp", "azure"
}

def extract_text_from_pdf(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_resume_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        return extract_text_from_pdf(path)
    if path.lower().endswith(".docx"):
        return extract_text_from_docx(path)
    raise ValueError("Unsupported resume format")

def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    return sorted({skill for skill in AIML_SKILLS if skill in text_lower})

def infer_years_experience(text: str) -> int:
    matches = re.findall(r"(\d+)\+?\s+years", text.lower())
    if not matches:
        return 0
    return max(int(m) for m in matches)

def infer_seniority(years: int) -> str:
    if years >= 6:
        return "senior"
    if years >= 3:
        return "mid"
    return "junior"

def infer_domains(text: str) -> List[str]:
    domains = []
    t = text.lower()

    if "nlp" in t or "language model" in t:
        domains.append("nlp")
    if "computer vision" in t or "image" in t:
        domains.append("cv")
    if "llm" in t or "genai" in t:
        domains.append("llm")
    if "recommendation" in t:
        domains.append("recsys")

    return domains

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def resume_intelligence_node(state: Dict[str, Any]) -> Dict[str, Any]:

    resume_path = state.get("resume_path")
    if not resume_path:
        raise RuntimeError("resume_path missing from state")

    raw_text = extract_resume_text(resume_path)

    skills = extract_skills(raw_text)
    years_experience = infer_years_experience(raw_text)
    seniority = infer_seniority(years_experience)
    domains = infer_domains(raw_text)

    resume_hash = hash_text(raw_text)
    candidate_id = state.get("candidate_id", "default")

    candidate_profile = {
        "_id": candidate_id,
        "skills": skills,
        "years_experience": years_experience,
        "seniority": seniority,
        "domains": domains,
        "updated_at": datetime.utcnow()
    }

    resume_artifact = {
        "file_path": resume_path,
        "hash": resume_hash,
        "raw_text": raw_text,
        "skills": skills,
        "domains": domains,
        "parsed_at": datetime.utcnow()
    }

    # ✅ DB
    save_candidate(candidate_id, candidate_profile)
    save_resume(resume_hash, resume_artifact)

    return {
        "candidate_profile": candidate_profile,
        "resume_artifact": resume_artifact
    }
