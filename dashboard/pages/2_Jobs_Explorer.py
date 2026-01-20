import streamlit as st
from db import get_jobs, get_job_quality

st.header("📄 Jobs Explorer")

jobs = get_jobs(limit=50)

job_titles = [
    f"{j['company']} — {j['title']}"
    for j in jobs
]

selected = st.selectbox("Select Job", job_titles)

job = jobs[job_titles.index(selected)]

st.subheader(job["title"])
st.write(job["company"], "•", job["location"])
st.write(job["description"][:1000])

quality = get_job_quality(job["job_id"])
if quality:
    st.markdown("### 🧪 Quality Evaluation")
    st.json(quality)
