import streamlit as st

def page_heading(title: str, subtitle: str = ""):
    st.markdown(f"<div class='eyebrow'>UDYAMONE · AIRTEL BUSINESS</div><h1>{title}</h1><p class='muted'>{subtitle}</p>", unsafe_allow_html=True)
