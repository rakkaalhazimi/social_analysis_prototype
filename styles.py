import streamlit as st

def set_style():
    st.markdown("""
    <style>
    div[data-baseweb="input"] > div > input {
                background-color: white;
            }
    </style>
    """, unsafe_allow_html=True)    