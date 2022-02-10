import streamlit as st

import config
from loader import load_data, load_trends_data, load_metric_data, load_tweet_style
from utils import remove_duplicates
from views import (
    show_logo, show_search_bar, show_tweet_trends, show_count_analysis_charts, show_tweet_count_chart,
    show_user_involvement_charts, show_tweet_details, show_wordcloud
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