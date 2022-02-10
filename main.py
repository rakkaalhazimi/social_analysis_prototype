import streamlit as st

import config
from loader import load_tweet_style
from views import (
    show_home, show_tweet_trends, show_count_analysis_charts, show_tweet_count_chart,
    show_user_involvement_charts, show_tweet_details, show_wordcloud
    )

# Streamlit settings
# st.set_page_config(layout="wide")

# Initial Load

load_tweet_style()

PAGES = {
    "Home": show_home,
    "Trend": show_tweet_trends,
    "Tweets Count": show_tweet_count_chart,
    "Count Analysis": show_count_analysis_charts,
    "User Involvement": show_user_involvement_charts,
    "Word Cloud": show_wordcloud,
    "Tweet Details": show_tweet_details}


# Sitebar
def change_page(page):
    run = PAGES.get(page)
    run()

page = st.sidebar.selectbox("", PAGES.keys())
change_page(page)


# Maintain the main display



# if "" not in queries:
if False:

    # Load trends data
    trends_df = load_trends_data(queries, df)
    
    # Show line chart
    show_tweet_trends(queries, trends_df)
    
    # Load metric data
    metric_df = load_metric_data(queries, df)

    # Show tweet count chart
    show_tweet_count_chart(metric_df[[config.TWEET_COUNT_COL]])
    
    # Show count analysis chart
    show_count_analysis_charts(metric_df[config.COUNT_ANALYSIS_COLS])
    
    # Show user involvement chart
    show_user_involvement_charts(metric_df[config.USER_INVOLVEMENT_COLS])
    
    # Show word cloud chart
    show_wordcloud(df, queries)
    
    
    # Show tweet details
    show_tweet_details(df, queries, max_tweets=30)