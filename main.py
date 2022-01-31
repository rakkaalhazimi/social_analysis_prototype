import streamlit as st

import config
from loader import load_data, load_trends_data, load_metric_data, load_tweet_style
from views import (
    set_bubble_charts, show_logo, show_search_bar, show_tweet_trends, show_count_analysis_charts, show_tweet_details
)

# Streamlit settings
st.set_page_config(layout="wide")

# Initial Load
df = load_data()
load_tweet_style()

# Maintain the main display
left, right = st.columns([2, 10])

with left: show_logo()
with right:
        queries = show_search_bar()

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
            # set_bubble_charts(0, 0, 0)
            st.subheader("")
            
            # Show count analysis chart
            st.subheader("Count Analysis")
            show_count_analysis_charts(metric_df[config.COUNT_ANALYSIS_COLS])
            st.subheader("")

            # Show user involvement chart
            st.subheader("User Involvement")
            show_count_analysis_charts(metric_df[config.USER_INVOLVEMENT_COLS])
            st.subheader("")
            
            # Show tweet details
            st.subheader("Tweet Details")
            show_tweet_details(df, queries, max_tweets=30)