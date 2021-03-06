from math import pi
from collections import namedtuple

from PIL import Image
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.transform import cumsum, dodge
from bokeh.models import (
    Div, DatetimeTickFormatter, Panel, Tabs, NumeralTickFormatter, 
    Label, LabelSet, ColumnDataSource, Legend, LegendItem
    )
from pyvis.network import Network

import config
from loader import (
    load_stopwords, load_transformed_charts_data, load_tweet_template, load_data, 
    load_trends_data, load_metric_data
    )
from utils import (
    arange_charts, color_generator, format_title, replace_wspace, remove_duplicates, 
    join_queries, filter_tweets, gen_wordcloud, split_relations, make_relations, trim_relations,
    cumsum_angle
    )


# Streamlit settings
st.set_page_config(layout="wide")

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
        value=queries or "Anies Baswedan, Ganjar Pranowo, Prabowo Subianto, Sandiaga Uno, Ridwan Kamil", 
        placeholder="Ex: Anies Baswedan, Ganjar Pranowo")
    return options.split(",")

def show_descriptions():
    st.write("""
    Harian Kompas merupakan aplikasi analisis sosial yang digunakan untuk melihat 
    tanggapan publik mengenai orang, kejadian atau objek tertentu melalui pencarian kata kunci.
    Pencarian dilakukan dengan menyaring data secara realtime dari beberapa sosial media terkenal seperti
    twitter dan instagram. Hasil dari data yang didapat kemudian disajikan dalam berbagai bentuk visualisasi
    diagram sehingga dapat membantu dalam proses analisa dan pengambilan keputusan. Selain visualisasi, aplikasi
    ini juga akan melakukan prediksi sentimen yang nantinya dapat dilihat untuk menilai bagaimana respon publik
    terhadap bahasan tertentu.
    """)

def show_home():
    show_logo("Harian Kompas")
    show_descriptions()

    st.subheader("Mulai Menggunakan")
    st.write("""
    Pengguna dapat memulai dengan memasukkan kata kunci terlebih dahulu. Setelah itu,
    pengguna dapat melihat hasil analisa pada panel navigasi di sebelah kiri.
    """)
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

Includes tweet trends and tweet count charts

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

        
        st.bokeh_chart(p)
        st.subheader("")


def show_tweet_count_chart():
    if st.session_state.get("queries") and st.session_state.get("metric_df") is not None:
        metric_df = st.session_state.get("metric_df")
        metric_df = load_transformed_charts_data(metric_df)

        if len(metric_df) >= 2:
            tooltips = [("query", "@category"), ("count", "@tweets_count{0,0}")]
            chart = set_vbar_chart(config.TWEET_COUNT_COL, tooltips, metric_df)
        else:
            chart = set_text_chart(300, 300, config.TWEET_COUNT_COL, metric_df)
        
        st.bokeh_chart(chart)
        st.subheader("")


def show_trend():
    st.subheader("Tweets Trends")
    st.write("""
    Tweet Trends adalah kecenderungan suatu bahasan untuk muncul ke permukaan. Tren digambarkan dengan
    jumlah tweet di setiap kata kunci dalam beberapa unit waktu (hari).
    """)
    show_tweet_trends()
    st.subheader("Tweets Count")
    st.write("""
    Tweet Count adalah keseluruhan jumlah tweet di setiap kata kunci.
    """)
    show_tweet_count_chart()

"""
==================================================================================
Content: Public Analysis
==================================================================================

Includes count analysis charts, user involvement charts and sentiment ratio

"""
def set_donut_charts(value_col, tooltips, source):
    angle_col = f"{value_col}_angle"
    source[angle_col] = source[value_col] / source[value_col].sum() * 2 * pi
    

    chart = figure(width=450, height=450, title=format_title(value_col), x_range=(-1, 1), y_range=(-1, 1), tooltips=tooltips, tools=[])
    wedge = chart.annular_wedge(
                    x=0, y=0, 
                    inner_radius=0.2, outer_radius=0.5,
                    start_angle=cumsum(angle_col, include_zero=True), 
                    end_angle=cumsum(angle_col),
                    legend_field=config.CATEGORY_COL,
                    fill_color=config.COLOR_COL,
                    line_color="white",
                    source=source)
    
    legend = Legend(items=[
        LegendItem(label=cat, renderers=[wedge], index=i) for i, cat in enumerate(source[config.CATEGORY_COL])
    ], orientation="horizontal")

    # chart.add_layout(legend, "above")

    source_copy = source.copy()
    source_copy = source_copy.query(f"{angle_col} > 0")
    source_copy[value_col] = source_copy[value_col] / source_copy[value_col].sum()
    source_copy[value_col] = source_copy[value_col].apply("{:.2%}".format).astype("str")
    source_copy["x"] = np.cos(cumsum_angle(source_copy[angle_col]) - source_copy[angle_col] / 2) / 1.5
    source_copy["y"] = np.sin(cumsum_angle(source_copy[angle_col]) - source_copy[angle_col] / 2) / 1.5

    source_copy = ColumnDataSource(source_copy)
    label = LabelSet(x="x", y="y", text=value_col, text_color="black", text_font_size="12px", source=source_copy, render_mode="canvas")
    chart.add_layout(label)

    chart.grid.grid_line_color = None
    chart.axis.axis_label = None
    chart.axis.visible = False
    chart.toolbar.logo = None
    chart.legend.label_text_font_size = "11px"
    chart.legend.padding = 0

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
            chart.legend.orientation = "vertical"
            chart.hover.mode = "mouse"
            
            
            # chart.background_fill_color = "#DAF7A6"

            charts.append(chart)

        layouts = arange_charts(charts, cols=2)
        grid_layout = column(*layouts)
        
        st.bokeh_chart(grid_layout)


def set_gauge_chart(row):
    chart = figure(width=300, height=300, y_range=(-0.5, 1), tools=[])

    positive_rad = row["positive_sentiment_count"] * pi
    negative_rad = row["negative_sentiment_count"] * pi

    source = ColumnDataSource(dict(neg_pos=[negative_rad, positive_rad], 
                                   color=["#D42B3A", "#2FD06A"],
                                   label=["Negatif", "Positif"]
                                   ))

    chart.annular_wedge(x=0, y=0, inner_radius=0.3, outer_radius=0.8,
                        start_angle=cumsum("neg_pos", include_zero=True), end_angle=cumsum("neg_pos"), 
                        color="color", legend_field="label", alpha=0.8, source=source)
    
    query_label = Label(x=130, y=30, x_units="screen", y_units="screen", text_font_style="bold",
                        text_align="center", text=row[config.CATEGORY_COL].center(30))
    chart.add_layout(query_label)

    positive_label = Label(x=60, y=70, x_units="screen", y_units="screen", 
                           text_align="center", text_color="#2FD06A",
                           text="{:.2%}".format(row["positive_sentiment_count"]))
    chart.add_layout(positive_label)

    negative_label = Label(x=210, y=70, x_units="screen", y_units="screen", 
                           text_align="center", text_color="#D42B3A",
                           text="{:.2%}".format(row["negative_sentiment_count"]))
    chart.add_layout(negative_label)
    
    chart.grid.grid_line_color = None
    chart.axis.axis_label = None
    chart.axis.visible = False
    chart.toolbar.logo = None

    return chart


def show_sentiment_count_charts():
    if st.session_state.get("queries") and st.session_state.get("metric_df") is not None:
        metric_df = st.session_state.get("metric_df")

        # Transform data
        metric_df = load_transformed_charts_data(metric_df)
        metric_df["sentiment_total"] = metric_df[config.COUNT_SENTIMENT_COLS].sum(axis=1)
        metric_df["positive_sentiment_count"] = metric_df["positive_sentiment_count"] / metric_df["sentiment_total"]
        metric_df["negative_sentiment_count"] = metric_df["negative_sentiment_count"] / metric_df["sentiment_total"]
        
        charts = []
        for _, row in metric_df.iterrows():
            # st.subheader(row[config.CATEGORY_COL])
            # st.metric("Positif", "{:.2%}".format(row["positive_sentiment_count"]))
            # st.metric("Negatif", "{:.2%}".format(row["negative_sentiment_count"]))
            charts.append(set_gauge_chart(row))
        
        row_charts = arange_charts(charts, cols=3)
        grid_layout = column(*row_charts)
        st.bokeh_chart(grid_layout)

        # tooltips = [
        #     ("query", "@category"), 
        #     ("Positif", "@{positive_sentiment_count}{%0.2f}"),
        #     ("Negatif", "@{negative_sentiment_count}{%0.2f}")
        # ]
        # chart = figure(width=900, height=300, y_range=metric_df[config.CATEGORY_COL], tools=[])
        # chart.hbar(y=config.CATEGORY_COL, left=0, height=0.2, right="positive_sentiment_count", color="#3BACC4", source=metric_df)
        # chart.hbar(y=config.CATEGORY_COL, left="positive_sentiment_count", height=0.2, right=1, color="#C4533B", source=metric_df)
        
        # chart.xaxis.visible = False
        # chart.yaxis.major_tick_line_color = None
        # chart.yaxis.major_label_text_font_size = "12px"
        # chart.grid.grid_line_color = None

        # st.bokeh_chart(chart)




def set_vbar_chart(value_col, tooltips, source):
    chart = figure(
        width=900, height=450, title=format_title(value_col), 
        x_range=source[config.CATEGORY_COL], 
        y_range=(0, 1.1 * source[value_col].max()), 
        tools=[], 
        tooltips=tooltips)

    chart.vbar(x=config.CATEGORY_COL, bottom=0, top=value_col, width=0.2, color=config.COLOR_COL, source=source)
    chart.yaxis[0].formatter = NumeralTickFormatter(format="0a")

    source_label = source.copy()
    source_label["value_text"] = source_label[value_col].astype(int).apply("{:,}".format)

    source_label = ColumnDataSource(source_label)
    labels = LabelSet(x=config.CATEGORY_COL, y=value_col, x_offset=-25, y_offset=10, text="value_text", source=source_label)
    chart.add_layout(labels)

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

        st.bokeh_chart(layout)
        


def show_public_analysis():

    st.subheader("Count Analysis")
    st.markdown("""
    Count Analysis merupakan perhitungan suatu aspek yang terdapat pada tweet. Aspek-aspek
    yang dimaksud meliputi:
    - **Viral Count**  
      Jumlah tweet yang viral. Tweet dianggap viral apabila jumlah reply, like atau retweet mencapai angka 1,000.
    - **Influencer Count**  
      Jumlah akun influencer. Akun dianggap sebagai influencer apabila jumlah followers yang dimiliki mencapai angka 1,000.
    - **Sensitive Count**
      Jumlah tweet yang sensitif. Tweet dianggap sensitif apabila konten dalam tweet dianggap tidak layak untuk dipertontonkan, 
      seperti kata-kata kasar dan kekerasan.
    """)
    show_count_analysis_charts()
    st.subheader("")

    st.subheader("User Involvement")
    st.markdown("""
    User Involvement merupakan tingkat keterlibatan pengguna dalam sebuah bahasan tweet. Jenis keterlibatan yang 
    dipakai terdiri dari:
    - **Interactions**  
      Jumlah interaksi pengguna pada tweet, ditentukan dengan melihat jumlah komentar dan jumlah retweet yang ditambahkan
      komentar.
    - **Potential User Reach**  
      Jumlah ketercapaian terhadap pengguna lain, ditentukan dengan melihat jumlah retweet dan like.
      
    """)
    show_user_involvement_charts()
    st.subheader("")

    st.subheader("Sentiment Ratio")
    st.markdown("""
    Sentimen Ratio adalah proporsi sentimen pada tiap kata kunci, menjelaskan bagaimana sikap publik terhadap
    suatu bahasan apakah cenderung positif atau negatif.
    """)
    show_sentiment_count_charts()

"""
==================================================================================
Content: Word Clouds
==================================================================================

Includes word cloud on every query

"""
def show_wordcloud():
    st.subheader("Word Cloud")
    st.markdown("""
    Word Cloud merupakan kumpulan kata yang digunakan oleh para pengguna media sosial. 
    Kata-kata ditampilkan dalam bentuk gambar yang berisikan yang mana memuat kata-kata yang sering
    muncul.
    """)

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
    st.markdown("""
    Tweet Details adalah bentuk asli dari tweet pengguna sosial media itu sendiri.
    """)
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


"""
==================================================================================
Content: Tweet Networks
==================================================================================

Includes tweet networks

"""
@st.cache
def get_node_edges(df, source, target, queries):
    Nodes = namedtuple("Node", "name color")
    Edges = namedtuple("Edge", "root leaf")

    df = df.copy()
    nodes, edges = [], []
    for color, q in zip(color_generator(), queries):
        # Temporary DataFrame
        filter_query = filter_tweets(df["full_text"], q)
        temp_df = df[filter_query].sort_values("user.followers_count", ascending=False)
        
        # Relations
        relations = make_relations(temp_df, source, target)
        relations["counts"] = relations[target].str.len()
        relations = relations.sort_values("counts", ascending=False).head(100)
        relations[target] = relations[target].apply(trim_relations)
        relations = split_relations(relations, target)

        for _, row in relations.iterrows():
            root = row["in_reply_to_screen_name"]
            leaf = row["user.screen_name"]
            
            nodes.append(Nodes(name=root, color=color))
            nodes.append(Nodes(name=leaf, color=color))
            edges.append(Edges(root=root, leaf=leaf))

    return nodes, edges

def build_network():

    social_net = Network(height="600px", width="900px", bgcolor="#111", font_color="#fff", directed=False)
    nodes, edges = get_node_edges(df, "in_reply_to_screen_name", "user.screen_name", st.session_state.get("queries"))

    for node in nodes:
        social_net.add_node(node.name, color=node.color, physics=False)

    for edge in edges:
        social_net.add_edge(edge.root, edge.leaf)

    social_net.barnes_hut()
    social_net.save_graph("src/template/social.html")
    
    HTMLfile = open("src/template/social.html", "r", encoding="utf-8")
    components.html(HTMLfile.read(), width=900, height=600)


def show_network():
    st.subheader("Social Network")
    st.write("""
    Social Network merupakan hubungan antar pengguna media sosial yang divisualisasikan dalam bentuk graph.
    Graph merupakan struktur data tidak linier yang terdiri dari node dan edge, yang mana node merepresentasikan
    pengguna dan edge merepresentasikan hubungan antar pengguna.
    """)
    if st.session_state.get("queries"):
        template = ""
        for color, q in zip(color_generator(), st.session_state.get("queries")):
            template += """
            <div>
              <span style="width: 10px; height: 10px; display: inline-block; background-color: {color}; border: 1px solid #000;">
              </span>
              <span>{query}</span>
            </div>
            """.format(query=q, color=color)
        st.markdown(template, unsafe_allow_html=True)
        build_network()
    