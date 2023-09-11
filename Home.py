import streamlit as st
import pandas as pd
import streamlit as st

st.set_page_config(page_title="CSGO Dashboard", page_icon=":gun:", 
    layout="wide", initial_sidebar_state="auto", menu_items=None)

about = open('README.md', 'r', encoding='utf8')
about = about.read().replace('./images/','https://raw.githubusercontent.com/TeoMinSi/csgo_tournament_tracker/main/images/')
st.markdown(about, unsafe_allow_html=True)
