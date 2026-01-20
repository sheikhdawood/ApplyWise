import streamlit as st
from db import get_applications, get_archives

st.header("🗂️ Archived Applications")

applications = get_applications()
archives = get_archives()

archived_job_ids = {a["job_id"] for a in archives}

archived_apps = [
    a for a in applications
    if a["job_id"] in archived_job_ids or a["status"] != "SUCCESS"
]

if not archived_apps:
    st.info("No archived or failed applications found.")
    st.stop()

st.dataframe([
    {
        "Job ID": a["job_id"],
        "Platform": a.get("platform"),
        "Status": a["status"],
        "Error": a.get("error"),
        "Applied At": a.get("applied_at")
    }
    for a in archived_apps
])
