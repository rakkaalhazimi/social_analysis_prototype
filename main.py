import streamlit as st

import config
from loader import load_data, load_trends_data, load_metric_data, load_tweet_style
from utils import remove_duplicates
from views import (
    show_logo, show_search_bar, show_tweet_trends, 
    show_metric_charts, show_tweet_details, show_wordcloud
    )

# Streamlit settings
st.set_page_config(layout="wide")

# Initial Load
df = load_data()
load_tweet_style()

# Maintain the main display
left, right = st.columns([3, 9])

with left: show_logo("Harian Kompas")
with right:
        queries = show_search_bar()
        queries = remove_duplicates(queries)

        if "" not in queries:

            # Load trends data
            trends_df = load_trends_data(queries, df)
            
            # Show line chart
            st.subheader("Tweets Trends")
            show_tweet_trends(queries, trends_df)
            st.subheader("")

            # Load metric data
            metric_df = load_metric_data(queries, df)

            # Show tweet count chart
            st.subheader("Tweets Count")
            show_metric_charts(metric_df[[config.TWEET_COUNT_COL]], mode="tweet_count")
            st.subheader("")
            
            # Show count analysis chart
            st.subheader("Count Analysis")
            show_metric_charts(metric_df[config.COUNT_ANALYSIS_COLS], mode="count_analysis")
            st.subheader("")

            # Show user involvement chart
            st.subheader("User Involvement")
            show_metric_charts(metric_df[config.USER_INVOLVEMENT_COLS], mode="user_involvement")
            st.subheader("")

            # Show word cloud chart
            st.subheader("Word Cloud")
            show_wordcloud(df, queries)
            st.subheader("")
            
            # Show tweet details
            st.subheader("Tweet Details")
            show_tweet_details(df, queries, max_tweets=30)