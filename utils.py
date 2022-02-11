import re
from itertools import cycle

import streamlit as st
from bokeh.layouts import row
from bokeh.palettes import Category10_10
from wordcloud import WordCloud


COLORS = Category10_10

def color_generator():
    for color in cycle(COLORS):
        yield color

def format_title(text):
    return text.replace("_", " ").title()

def format_date(row_date):
    return row_date.strftime("%Y-%m-%d")

def replace_wspace(text):
    return text.replace(" ", "_")


@st.cache
def filter_tweet_count(series, query):
    return series.str.contains(query, flags=re.IGNORECASE).sum()

@st.cache
def filter_tweets(df, query):
    return df.str.contains(query, flags=re.IGNORECASE)


@st.cache(allow_output_mutation=True)
def make_relations(df, source, target):
    df = df.copy()
    relations = df.groupby(source, as_index=False).agg({target: list})
    return relations

@st.cache
def split_relations(relations, target):
    return relations.explode(target)

def trim_relations(array):
    return array[:3]


@st.cache
def gen_wordcloud(text, **kwargs):
    return WordCloud(**kwargs).generate(text)

def join_queries(queries):
    if queries is None:
        return False
    else:
        return ",".join(queries)

def remove_duplicates(items):
    item_list = []
    filtered = []
    for item in items:
        if item in item_list:
            continue
        filtered.append(item)
        item_list.append(item)
    return filtered
        

def arange_charts(charts, cols=3):
    layouts = []
    for i in range(0, len(charts), cols):
        layouts.append(row(*charts[i:i + cols]))
    return layouts