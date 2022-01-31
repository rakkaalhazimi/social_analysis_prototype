from math import pi

from bokeh.plotting import figure
from bokeh.layouts import row
from bokeh.transform import cumsum

from utils import format_title


def arange_charts(charts, cols=3):
    layouts = []
    for i in range(0, len(charts), cols):
        layouts.append(row(*charts[i:i + cols]))
    return layouts

def set_donut_charts(chart, value_col, category_col, color_col, tooltips, source):
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
    chart.grid.grid_line_color = None
    
    return chart


def set_hbar_chart(queries, value_col, category_col, color_col, tooltips, source):
    chart = figure(width=300, height=300, title=format_title(value_col), tools=[], tooltips=tooltips)
    chart.hbar(y=["anies", "prabowo", "zeyakan"], left=0, right=[1, 2, 3], height=0.2, source=source)
    return chart


def set_text_chart(value_col, source):
    digit = int(source[value_col])
    chart = figure(width=300, height=300, title=format_title(value_col), tools=[])
    chart.text(x=0, y=1, text=["{:,}".format(digit)], 
                text_baseline="middle", text_align="center", text_font_size="20px", text_font_style="bold")
    chart.toolbar.tools = []
    chart.toolbar_location = None
    return chart