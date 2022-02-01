import re
from itertools import cycle

from bokeh.layouts import row
from bokeh.palettes import Bokeh8


COLORS = Bokeh8

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