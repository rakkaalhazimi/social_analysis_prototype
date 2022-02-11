import pandas as pd
import streamlit as st
import nltk
from nltk.corpus import stopwords
nltk.download("stopwords")


import config
from metrics import tweet_trends, query_metric, all_counts, user_involvement
from utils import color_generator


@st.cache
def load_data():
    return pd.read_csv(config.DATA_PATH, parse_dates=[config.DATE_COL], index_col=config.DATE_COL)

@st.cache
def load_trends_data(queries, df):
    return tweet_trends("1D", queries, df)

@st.cache(allow_output_mutation=True)
def load_metric_data(queries, df):
    # Get metrics DataFrame
    metrics_df = query_metric(queries, df)

    # Get counts DataFrame
    counts_df = all_counts(df, queries)

    # Concat both metrics and counts
    metric_count_df = pd.concat([metrics_df, counts_df], axis=1)

    # Create user involvement DataFrame
    user_df = user_involvement(metric_count_df)

    # Return last concatenated DataFrame
    return user_df

@st.cache(allow_output_mutation=True)
def load_transformed_charts_data(df):
    len_data = df.shape[0]
    color_gen = color_generator()

    # Transform data
    df[config.CATEGORY_COL] = df.index
    df[config.COLOR_COL] = [next(color_gen) for i in range(len_data)]

    return df

@st.cache(allow_output_mutation=True)
def load_network_data(df):
    relations = df.groupby("in_reply_to_status_id_str").agg({"id_str": list})
    relations = relations.head(100).explode("id_str")


@st.cache
def load_tweet_template():
    with open(config.TWEET_TEMPLATE_PATH, "r") as template:
        return template.read()

def load_tweet_style():
    with open(config.TWEET_STYLE_PATH, "r") as style:
        st.markdown(style.read(), unsafe_allow_html=True)

@st.cache
def load_stopwords():
    return stopwords.words("indonesian")