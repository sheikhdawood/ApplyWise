import streamlit as st

st.header("⚙️ System Control")

st.warning("These controls affect automation behavior.")

kill = st.checkbox("🚨 Global Kill Switch")

if kill:
    st.error("Automation paused. Agent should not run.")
