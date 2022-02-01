import re
from math import pi, ceil

import streamlit as st

from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import (
    Div, DatetimeTickFormatter, Panel, Tabs
)
from bokeh.transform import cumsum
from bokeh.palettes import Bokeh5

import config
from loader import load_transformed_charts_data, load_tweet_template
from metrics import (
    replace_wspace
)
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
    tooltips = [("Date", "@date{%F}")] + [(f"{query}", f"@{replace_wspace(query)}" + "{0,0}") for query in queries]

    p = figure(width=900, height=420, x_axis_type="datetime", tooltips=tooltips, title="Tweets Trend")

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
Content: Tweet Count Charts
==================================================================================

Includes tweet count charts

"""
def set_bubble_charts(value_col, source):

    # Transform data
    source = load_transformed_charts_data(source)
    
    data = source[value_col]

    width = 900
    height = 420
    cols = 3
    rows = ceil(len(data) / cols)
    y_pad = (width // height) * 2 / 10
    x_range = (-1, cols)
    y_range = (-(y_pad * rows) + 0.2, 0 + 0.2)
    tooltips = [("query", f"@{config.CATEGORY_COL}"), ("counts", f"@{value_col}")]

    chart = figure(width=width, height=height, x_range=x_range, y_range=y_range, tools=[], tooltips=tooltips)

    x, y = [], []
    row, col = 0, 0
    sizes = [value / sum(data) * (width // 2) for value in data]

    for i in range(len(data)):
        x.append(col)
        y.append(row)

        if col == cols - 1:
            col = 0
            row -= y_pad
        else:
            col += 1

    source["x"], source["y"], source["sizes"] = x, y, sizes

    chart.hex(x="x", y="y", legend_field=config.CATEGORY_COL, size="sizes", color=config.COLOR_COL, source=source)

    chart.axis.axis_label=None
    chart.axis.visible=False
    chart.grid.grid_line_color = None
    return chart


def show_tweet_count_chart(metric_df):
    metric_names = metric_df.columns
    if len(metric_names) >= 2:
        chart = set_bubble_charts(config.TWEET_COUNT_COL, metric_df)
    else:
        chart = set_text_chart(300, 300, config.TWEET_COUNT_COL, metric_df)
    
    return chart


"""
==================================================================================
Content: Count Analysis Charts
==================================================================================

Includes count analysis charts

"""
def set_donut_charts(value_col, tooltips, source):
    angle_col = f"{value_col}_angle"
    source[angle_col] = source[value_col] / source[value_col].sum() * 2 * pi

    chart = figure(width=300, height=300, title=format_title(value_col), tools=[], tooltips=tooltips)
    chart.annular_wedge(
                x=0, y=1, 
                inner_radius=0.2, outer_radius=0.5,
                start_angle=cumsum(angle_col, include_zero=True), 
                end_angle=cumsum(angle_col),
                legend_field=config.CATEGORY_COL,
                fill_color=config.COLOR_COL,
                line_color="white",
                source=source)

    chart.grid.grid_line_color = None
    chart.axis.axis_label = None
    chart.axis.visible = False
    chart.toolbar.logo = None
    chart.toolbar_location = None

    return chart


def set_text_chart(width, height, value_col, source):
    digit = int(source[value_col])
    chart = figure(width=width, height=height, title=format_title(value_col), tools=[])
    chart.text(x=0, y=1, text=["{:,}".format(digit)], 
                text_baseline="middle", text_align="center", text_font_size="20px", text_font_style="bold")

    chart.grid.grid_line_color = None
    chart.axis.axis_label = None
    chart.axis.visible = False
    chart.toolbar.logo = None
    chart.toolbar_location = None

    return chart


def show_count_analysis_charts(metric_df):
    charts = []
    metric_names = metric_df.columns

    # Transform data
    metric_df = load_transformed_charts_data(metric_df)

    for _, value_col in enumerate(metric_names):
        tooltips = [("query", "@category"), (f"{value_col}", "@" + value_col + "{0,0}")]

        if len(metric_df) >= 2:
            chart = set_donut_charts(value_col, tooltips, metric_df)

        else:
            chart = set_text_chart(300, 300, value_col, metric_df)
            
        # Chart Properties
        
        chart.legend.location = "bottom_left"
        chart.legend.orientation = "horizontal"
        chart.hover.mode = "mouse"
        
        
        # chart.background_fill_color = "#DAF7A6"

        charts.append(chart)

    layouts = arange_charts(charts, cols=3)
    grid_layout = column(*layouts)
    return grid_layout


"""
==================================================================================
Content: User Involvement Charts
==================================================================================

Includes user involvement charts

"""
def set_vbar_chart(value_col, tooltips, source):
    chart = figure(
        width=900, height=300, title=format_title(value_col), 
        x_range=source[config.CATEGORY_COL], tools=[], tooltips=tooltips)
    chart.vbar(x=config.CATEGORY_COL, bottom=0, top=value_col, width=0.2, color=config.COLOR_COL, source=source)
    return chart


def show_user_involvement_charts(metric_df):
    charts = []
    metric_names = metric_df.columns

    # Transform data
    metric_df = load_transformed_charts_data(metric_df)

    for _, value_col in enumerate(metric_names):
        tooltips = [("query", "@category"), (f"{value_col}", "@" + value_col + "{0,0}")]

        if len(metric_df) >= 2:
            chart = set_vbar_chart(value_col, tooltips, metric_df)
            charts.append(chart)
            charts.append(Div(height=100))

        else:
            chart = set_text_chart(300, 300, value_col, metric_df)
            charts.append(chart)

    if len(metric_df) >= 2:
        layout = column(*charts)
    else:
        layout = arange_charts(charts, cols=3)
        layout = column(*layout)

    return layout


"""
==================================================================================
Wrap All Metrics
==================================================================================

Controller to show metric charts

"""

def show_metric_charts(metric_df, mode):
    # Initiate parameter
    mode_charts = {
        "tweet_count": show_tweet_count_chart,
        "count_analysis": show_count_analysis_charts,
        "user_involvement": show_user_involvement_charts
    }

    

    # Show chart
    chart = mode_charts[mode](metric_df)
    st.bokeh_chart(chart)


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
                width=900, sizing_mode="scale_width")
            
            tweet_list.append(tweet_card)

        panels.append( Panel(child=column(*tweet_list), title=query) )
    
    layouts = Tabs(tabs=panels)
    st.bokeh_chart(layouts)