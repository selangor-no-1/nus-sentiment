import altair as alt
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud, STOPWORDS  
import matplotlib.pyplot as plt
import random 

def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    brightness = random.randint(44,70)
    color = random.choice(['40','226'])
    return "hsl(" + color + ", 97%, " + str(brightness) + "%)"

def wordcloudchart(data: pd.DataFrame):
        all_post_string = data['post'].sum()
        stopwords = set(STOPWORDS)
        stopwords.update(['a', 'b', 'c', 'u', 'C', 'want', 'know', 'take', 'think', 's', 'took', 'one', 'will', 'prof', 'lot', 'much', 'need'])
        fig, ax = plt.subplots(figsize=(15,5))
        wc = WordCloud(stopwords = stopwords, background_color = "white", max_words = 20)
        wc.generate(all_post_string)
        plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3), interpolation='bilinear')
        plt.axis("off")
        plt.show()
        return fig

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



