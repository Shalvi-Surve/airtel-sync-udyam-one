import streamlit as st

def navigation(labels, language="English"):
    with st.sidebar:
        st.markdown("<div class='brand'>UdyamOne.</div>", unsafe_allow_html=True)
        return st.radio("Workspace", labels, label_visibility="collapsed", format_func=lambda key: language.get(key, key))
