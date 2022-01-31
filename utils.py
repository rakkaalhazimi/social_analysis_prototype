import re
from itertools import cycle

import streamlit as st
from bokeh.layouts import row
from bokeh.palettes import Category10_10, Spectral


COLORS = Spectral[11]

def color_generator():
    for color in cycle(COLORS):
        yield color

def format_title(text):
    return text.replace("_", " ").title()

def format_date(row_date):
    return row_date.strftime("%Y-%m-%d")

def replace_wspace(text):
    return text.replace(" ", "_")

def filter_tweet_count(series, query):
    return series.str.contains(query, flags=re.IGNORECASE).sum()

def arange_charts(charts, cols=3):
    layouts = []
    for i in range(0, len(charts), cols):
        layouts.append(row(*charts[i:i + cols]))
    return layouts