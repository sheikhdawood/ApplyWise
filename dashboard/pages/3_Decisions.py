import streamlit as st
from db import get_decisions

st.header("🎯 Application Decisions")

decisions = get_decisions()

st.dataframe([
    {
        "Job ID": d["job_id"],
        "Action": d["action"],
        "Confidence": d["confidence"],
        "Human Required": d["requires_human"],
        "Time": d["decided_at"]
    }
    for d in decisions
])
