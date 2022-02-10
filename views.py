import re
from math import pi, ceil

from PIL import Image
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.transform import cumsum
from bokeh.models import (
    Div, DatetimeTickFormatter, Panel, Tabs
    )


import config
from loader import load_stopwords, load_transformed_charts_data, load_tweet_template, load_data, load_trends_data, load_metric_data, load_tweet_style
from utils import arange_charts, color_generator, format_title, replace_wspace, remove_duplicates, join_queries, filter_tweets, gen_wordcloud


# Load Data
df = load_data()

"""
==================================================================================
Header
==================================================================================

Includes search bar and logo

"""
def show_logo(title):
    st.title(title)

def show_search_bar():
    queries = join_queries(st.session_state.get("queries"))
    options = st.text_input(
        label="Masukkan Nama Lengkap", 
        value=queries or "Anies Baswedan", 
        placeholder="Ex: Anies Baswedan, Ganjar Pranowo")
    return options.split(",")

def show_home():
    show_logo("Harian Kompas")

    queries = show_search_bar()
    queries = remove_duplicates(queries)
    if "" not in queries:
        st.session_state["queries"] = queries
        st.session_state["metric_df"] = load_metric_data(st.session_state["queries"], df)
        st.session_state["trends_df"] = load_trends_data(st.session_state["queries"], df)

"""
==================================================================================
Content: Tweet Trends
==================================================================================

Includes tweet trends

"""

# Timeline Chart
def show_tweet_trends():
    if st.session_state.get("queries") and st.session_state.get("trends_df") is not None:
        trends = st.session_state["trends_df"]
        queries = st.session_state["queries"]

        tooltips = [("Date", "@date{%F}")] + [(f"{query}", f"@{replace_wspace(query)}" + "{0,0}") for query in queries]

        p = figure(width=900, height=420, x_axis_type="datetime", tools=[], tooltips=tooltips, title="Tweets Trend")

        for query, color in zip(queries, color_generator()):
            p.line(x="date", y=replace_wspace(query), legend_label=query, color=color, source=trends)
            p.scatter(x="date", y=replace_wspace(query), legend_label=query, color=color, source=trends)

        p.xaxis.major_label_orientation = "horizontal"
        p.xaxis.formatter = DatetimeTickFormatter(days="%Y-%m-%d")
        p.hover.formatters = {"@date": "datetime"}
        p.legend.location = "top_left"
        p.legend.background_fill_alpha = 0.3

        st.subheader("Tweets Trends")
        st.bokeh_chart(p)
        st.subheader("")


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


def show_tweet_count_chart():
    if st.session_state.get("queries") and st.session_state.get("metric_df") is not None:
        metric_df = st.session_state.get("metric_df")

        if len(metric_df) >= 2:
            chart = set_bubble_charts(config.TWEET_COUNT_COL, metric_df)
        else:
            chart = set_text_chart(300, 300, config.TWEET_COUNT_COL, metric_df)
        
        st.subheader("Tweets Count")
        st.bokeh_chart(chart)
        st.subheader("")


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


def show_count_analysis_charts():
    if st.session_state.get("queries") and st.session_state.get("metric_df") is not None:
        charts = []
        metric_df = st.session_state.get("metric_df")
        metric_names = config.COUNT_ANALYSIS_COLS

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
        
        st.subheader("Count Analysis")
        st.bokeh_chart(grid_layout)
        st.subheader("")


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


def show_user_involvement_charts():
    if st.session_state.get("queries") and st.session_state.get("metric_df") is not None:
        charts = []
        metric_df = st.session_state.get("metric_df")
        metric_names = config.USER_INVOLVEMENT_COLS

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


        st.subheader("User Involvement")
        st.bokeh_chart(layout)
        st.subheader("")


"""
==================================================================================
Content: Word Clouds
==================================================================================

Includes word cloud on every query

"""
def show_wordcloud():
    st.subheader("Word Cloud")

    if st.session_state.get("queries"):
        queries = st.session_state.get("queries")
        mask = np.array(Image.open("src/images/twitter.jpg"))
        stopwords = load_stopwords() + ["yg", "nya"]
        
        for query in queries:
            fig = plt.figure(figsize=(8, 8))

            # Filter data
            filters = filter_tweets(df[config.TEXT_COL], query)
            sorted_df = df[filters].sort_values(by=[config.REPLY_COL]).head(200)
            text = sorted_df[config.TEXT_CLEAN_COL].str.cat(sep=" ")

            wcloud = gen_wordcloud(
                text,
                background_color="white",
                max_words=1000,
                mask=mask,
                stopwords=stopwords,
            )

            plt.imshow(wcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title(f"{query} words", fontdict=dict(fontsize=10))

            
            st.pyplot(fig)
            st.subheader("")


"""
==================================================================================
Content: Tweet Details
==================================================================================

Includes tweet from user

"""
def show_tweet_details():
    st.subheader("Tweet Details")
    max_tweets = 30
    
    if st.session_state.get("queries"):
        queries = st.session_state.get("queries")
        panels = []

        for query in queries:
            tweet_list = []

            # Filter data
            filter = filter_tweets(df[config.TEXT_COL], query)
            filtered_df = df[filter]

            # Sort data
            filtered_df = filtered_df.sort_values(by=[config.REPLY_COL], ascending=False)
            filtered_df[config.DATE_COL] = filtered_df.index.strftime("%d %B %Y")
            filtered_df = filtered_df.reset_index(drop=True).fillna(0)

            for index, row in filtered_df.iterrows():
                if index > max_tweets:
                    break
                
                template = load_tweet_template().format(
                    name=row[config.USERNAME_COL],
                    date=row[config.DATE_COL],
                    content=row[config.TEXT_COL],
                    sentiment=row[config.SENTIMENT_COL],
                    reply=int( row[config.REPLY_COL] ),
                    retweet=int( row[config.RETWEET_COL] ),
                    like=int( row[config.LIKE_COL] ),
                )

                tweet_card = Div(
                    text=template, 
                    width=900, sizing_mode="scale_width")
                
                tweet_list.append(tweet_card)

            panels.append( Panel(child=column(*tweet_list), title=query) )
        
        layouts = Tabs(tabs=panels)
        st.bokeh_chart(layouts)