import streamlit as st
from loader import load_data, load_trends_data, load_metric_data, load_tweet_style
from views import (
    show_logo, show_search_bar, show_tweet_trends, show_metric_charts, show_tweet_details
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
            st.subheader("Tweets Timeline")
            show_tweet_trends(queries, trends_df)
            st.subheader("")

            # Load metric data
            metric_df = load_metric_data(queries, df)
            
            # Show metrics chart
            st.subheader("Tweet Metrics")
            show_metric_charts(metric_df)
            st.subheader("")
            
            # Show tweet details
            st.subheader("Tweet Details")
            # show_tweet_details(df, queries, max_tweets=30)