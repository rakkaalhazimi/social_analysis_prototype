import re
from math import pi

import streamlit as st

from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import (
    Div, DatetimeTickFormatter, Panel, Tabs
)
from bokeh.transform import cumsum

import config
from loader import load_tweet_template
from metrics import (
    replace_wspace
)
from plots import set_hbar_chart, set_donut_charts, set_text_chart
from utils import arange_charts, color_generator, format_title


"""
==================================================================================
Header
==================================================================================

Includes search bar and logo

"""
def show_logo():
    st.subheader("Bangalore")

def show_search_bar():
    options = st.text_input(label="Enter keywords", value="anies", placeholder="Ex: anies, ganjar, prabowo")
    return options.split(",")



"""
==================================================================================
Content: Tweet Trends
==================================================================================

Includes tweet trends

"""

# Timeline Chart
def show_tweet_trends(queries, trends):
    tooltips = [("Date", "@date{%F}")] + [(f"{query}", f"@{replace_wspace(query)}") for query in queries]

    p = figure(width=900, height=500, x_axis_type="datetime", tooltips=tooltips, title="Tweets Trend")

    for query, color in zip(queries, color_generator()):
        p.line(x="date", y=replace_wspace(query), legend_label=query, color=color, source=trends)
        p.scatter(x="date", y=replace_wspace(query), legend_label=query, color=color, source=trends)

    p.xaxis.major_label_orientation = "horizontal"
    p.xaxis.formatter = DatetimeTickFormatter(days="%Y-%m-%d")
    p.hover.formatters = {"@date": "datetime"}
    p.legend.location = "top_left"
    p.legend.background_fill_alpha = 0.3

    st.bokeh_chart(p)


"""
==================================================================================
Content: Metric Charts
==================================================================================

Includes tweet metric charts

"""
def set_donut_charts(value_col, tooltips, source):
    chart = figure(width=300, height=300, title=format_title(value_col), tools=[], tooltips=tooltips)

    angle_col = f"{value_col}_angle"
    source[angle_col] = source[value_col] / source[value_col].sum() * 2 * pi

    chart = figure(width=300, height=300, title=format_title(value_col), tools=[], tooltips=tooltips)
    chart.annular_wedge(
                x=0, y=1, 
                inner_radius=0.4, outer_radius=0.5,
                start_angle=cumsum(angle_col, include_zero=True), 
                end_angle=cumsum(angle_col),
                legend_field="category",
                color="color",
                source=source)
    
    chart.axis.axis_label=None
    chart.axis.visible=False

    return chart


def set_hbar_chart(value_col, tooltips, source):
    chart = figure(
        width=600, height=300, title=format_title(value_col), 
        y_range=source[config.CATEGORY_COL], tools=[], tooltips=tooltips)
    chart.hbar(y=config.CATEGORY_COL, left=0, right=value_col, height=0.2, source=source)
    return chart


def set_text_chart(value_col, source):
    digit = int(source[value_col])
    chart = figure(width=300, height=300, title=format_title(value_col), tools=[])
    chart.text(x=0, y=1, text=["{:,}".format(digit)], 
                text_baseline="middle", text_align="center", text_font_size="20px", text_font_style="bold")

    chart.toolbar.tools = []
    chart.toolbar_location = None
    chart.axis.axis_label=None
    chart.axis.visible=False
    
    return chart


def show_metric_charts(metric_df):
    # Initiate parameter
    charts = []
    len_data = metric_df.shape[0]
    color_gen = color_generator()
    color_col = "color"
    category_col = "category"
    metric_names = metric_df.columns

    # Transform data
    metric_df[category_col] = metric_df.index
    metric_df[color_col] = [next(color_gen) for i in range(len_data)]

    for index, value_col in enumerate(metric_names):
        tooltips = [("query", "@category"), (f"{value_col}", "@" + value_col + "{0,0}")]

        if len(metric_df) >= 2:
            if index < 3:
                chart = set_donut_charts(value_col, tooltips, metric_df)
            else:
                chart = set_hbar_chart(value_col, tooltips, metric_df)

        else:
            chart = set_text_chart(value_col, metric_df)
            
        # All Chart Properties
        chart.toolbar.logo = None
        chart.legend.location = "bottom_left"
        chart.legend.orientation = "horizontal"
        chart.hover.mode = "mouse"
        
        chart.grid.grid_line_color = None
        # chart.background_fill_color = "#DAF7A6"

        charts.append(chart)

    layouts = arange_charts(charts, cols=3)
    grid_layout = column(*layouts)
    st.bokeh_chart(grid_layout)


"""
==================================================================================
Content: Tweet Details
==================================================================================

Includes tweet from user

"""
def show_tweet_details(df, queries, max_tweets):
    panels = []

    for query in queries:
        tweet_list = []
        filter = df[config.TEXT_COL].str.contains(query, flags=re.IGNORECASE)
        filtered_df = df[filter]
        filtered_df[config.DATE_COL] = filtered_df.index.strftime("%d %B %Y")
        filtered_df = filtered_df.reset_index(drop=True).fillna(0)

        for index, row in filtered_df.iterrows():
            if index > max_tweets:
                break
            
            template = load_tweet_template().format(
                name=row[config.USERNAME_COL],
                date=row[config.DATE_COL],
                content=row[config.TEXT_COL],
                reply=int( row[config.REPLY_COL] ),
                retweet=int( row[config.RETWEET_COL] ),
                like=int( row[config.LIKE_COL] )
            )

            tweet_card = Div(
                text=template, 
                # style={"border": "2px solid red"}, 
                width=900, sizing_mode="scale_width")
            
            tweet_list.append(tweet_card)

        panels.append( Panel(child=column(*tweet_list), title=query) )
    
    layouts = Tabs(tabs=panels)
    st.bokeh_chart(layouts)