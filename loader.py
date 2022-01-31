import pandas as pd
import streamlit as st

import config
from metrics import tweet_trends, query_metric, all_counts, made_variables


@st.cache
def load_data():
    return pd.read_csv(config.DATA_PATH, parse_dates=[config.DATE_COL], index_col=config.DATE_COL)


def load_trends_data(queries, df):
    return tweet_trends("1D", queries, df)


def load_metric_data(queries, df):
    # Get metrics DataFrame
    metrics_df = query_metric(queries, df)

    # Get counts DataFrame
    counts_df = all_counts(df, queries)

    # Concat both metrics and counts
    metric_count_df = pd.concat([metrics_df, counts_df], axis=1)

    # Create made DataFrame
    made_df = made_variables(metric_count_df)

    # Return count and made DataFrame
    config.EXCLUDE_COLS += list(metrics_df.columns)
    return  made_df.drop(config.EXCLUDE_COLS, axis=1)


def load_charts_data():
    return


def load_tweet_template():
    with open(config.TWEET_TEMPLATE_PATH, "r") as template:
        return template.read()

def load_tweet_style():
    with open(config.TWEET_STYLE_PATH, "r") as style:
        st.markdown(style.read(), unsafe_allow_html=True)