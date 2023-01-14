import altair as alt
import plotly.express as px
import pandas as pd

def bar(counts: dict):
    fig = px.bar(x=list(counts.keys()), y=list(counts.values()), color=list(counts.keys()))
    return fig

def line_and_scatter(data: pd.DataFrame, keyword: str):
    chart = alt.Chart(data, title=f"Sentiment Over Time for {keyword}")

    line = chart.mark_line(tooltip=True).encode(
        x=alt.X("created_at:T", timeUnit="yearmonthdate", title="time"),
        y=alt.Y(
            "mean(sentiment):Q", title="sentiment", scale=alt.Scale(domain=[-1,1])
        ),
        color=alt.Color(value="#FF4B4B")
    )

    scatter = chart.mark_point(size=75, filled=True).encode(
        x=alt.X("created_at:T", timeUnit="yearmonthdate", title="time"),
        y=alt.Y("sentiment:Q", title="sentiment"),
        tooltip=alt.Tooltip(["created_at", "sentiment", "post"])
    )

    return line + scatter