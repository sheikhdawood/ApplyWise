import streamlit as st
import pandas as pd
from db import (
    get_jobs,
    get_decisions,
    get_applications,
    get_trust_states
)

st.header("📊 Analytics")

jobs = get_jobs()
decisions = get_decisions()
applications = get_applications()
trusts = get_trust_states()

# ---------- BASIC COUNTS ----------
st.subheader("📈 System Volume")

col1, col2, col3 = st.columns(3)
col1.metric("Jobs Discovered", len(jobs))
col2.metric("Decisions Made", len(decisions))
col3.metric("Applications Sent", len(applications))

# ---------- DECISION DISTRIBUTION ----------
st.subheader("🎯 Decision Breakdown")

if decisions:
    df_dec = pd.DataFrame(decisions)
    decision_counts = df_dec["action"].value_counts()
    st.bar_chart(decision_counts)
else:
    st.info("No decisions yet.")

# ---------- APPLICATION RESULTS ----------
st.subheader("🚀 Application Outcomes")

if applications:
    df_app = pd.DataFrame(applications)
    status_counts = df_app["status"].value_counts()
    st.bar_chart(status_counts)
else:
    st.info("No applications yet.")

# ---------- TRUST ANALYTICS ----------
st.subheader("🧠 Platform Trust")

for t in trusts:
    st.markdown(f"### {t['platform']}")
    st.metric("Trust Score", t["trust_score"])
    st.write("Automation Level:", t["automation_level"])
    st.json(t["signals"])
