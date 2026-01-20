import streamlit as st
from db import get_holds

st.header("⏸️ Jobs on Hold")

holds = get_holds()

for h in holds:
    with st.expander(f"{h['company']} — {h['title']}"):
        st.write("Reasons:")
        st.write(h["reason"])
        st.write("Review After Days:", h["review_after_days"])
