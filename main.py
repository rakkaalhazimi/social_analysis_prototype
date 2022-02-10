import streamlit as st

import config
from loader import load_tweet_style
from views import (
    show_home, show_trend, show_public_analysis, show_tweet_details, show_wordcloud
    )

# Streamlit settings
# st.set_page_config(layout="wide")

# Initial Load

load_tweet_style()

PAGES = {
    "Home": show_home,
    "Trends": show_trend,
    "Public Analysis": show_public_analysis,
    "Word Cloud": show_wordcloud,
    "Tweet Details": show_tweet_details}


# Sitebar
def change_page(page):
    run = PAGES.get(page)
    run()

page = st.sidebar.selectbox("", PAGES.keys())
change_page(page)