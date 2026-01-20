import streamlit as st
from db import get_trust_states

st.header("🧠 Platform Trust State")

trusts = get_trust_states()

for t in trusts:
    st.subheader(t["platform"])
    st.metric("Trust Score", t["trust_score"])
    st.write("Automation Level:", t["automation_level"])
    st.json(t["signals"])
