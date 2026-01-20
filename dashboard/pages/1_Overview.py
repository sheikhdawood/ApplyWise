import streamlit as st
from db import (
    get_jobs, get_applications,
    get_decisions, get_holds
)

st.header("📊 System Overview")

jobs = get_jobs()
apps = get_applications()
decisions = get_decisions()
holds = get_holds()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Jobs Discovered", len(jobs))
col2.metric("Applications Sent", len(apps))
col3.metric("Decisions Made", len(decisions))
col4.metric("Jobs on Hold", len(holds))

st.divider()

st.subheader("Recent Applications")
st.table([
    {
        "Company": a.get("platform"),
        "Status": a["status"],
        "Time": a["applied_at"]
    }
    for a in apps[:5]
])
