import streamlit as st
import praw
import os
from dotenv import load_dotenv
import pandas as pd
from utils.model import download_model, LABELS
import plotly.express as px
from components.post_card import post_card
import transformers
from datetime import datetime
import altair as alt

st.markdown("<h1>NUS Sentiment</h1>", unsafe_allow_html=True)

load_dotenv()

client_id = os.getenv('ACCESS_TOKEN')
client_secret = os.getenv('SECRET_KEY')
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
user_agent = "dev"

reddit = praw.Reddit(
    client_id = client_id,
    client_secret = client_secret,
    user_agent = user_agent,
    username = username,
    password = password
)

nus_sub = reddit.subreddit("nus")

_, _, nlp  = download_model()

st.header("Scrape posts from r/NUS")

@st.experimental_memo(ttl=60*60)
def scrape(keyword: str):
    data = []

    for post in nus_sub.search(keyword):
        comments = post.comments
        comments_list = comments.list()

        # add the body of the post itself
        data.append((post.title, post.author, datetime.fromtimestamp(post.created_utc), post.selftext))

        # BFS
        while len(comments_list) > 0:
            comment = comments_list.pop(0)
            if not isinstance(comment, praw.models.MoreComments) and comment.author != "AutoModerator":
                data.append((post.title, comment.author, datetime.fromtimestamp(comment.created_utc), comment.body))
            elif isinstance(comment, praw.models.MoreComments):
                comments_list.extend(comment.comments())
        
    return pd.DataFrame(data, columns=["thread_title", "author", "created_at","post"])

cache_args = dict(
    show_spinner = True,
    allow_output_mutation = True,
    suppress_st_warning=True,
    hash_funcs = {
        pd.DataFrame: lambda x: None,
        transformers.pipelines.text_classification.TextClassificationPipeline: lambda x: None,
    },
)

@st.cache(ttl=60*60, **cache_args)
def get_sentiment(nlp, posts):
    sentiments = nlp(posts)

    l = [LABELS[x["label"]] for x in sentiments]
    s = [x["score"] for x in sentiments]

    return list(zip(l,s))

def count_sentiment(result):
    sentiments = {"negative":0, "neutral":0, "positive":0}
    for sentiment, _ in result:
        sentiments[sentiment] += 1
    return sentiments

with st.form("scraper"):

    keyword = st.text_input(label="Input the keyword you wish to search for", placeholder="CS1010S")
    remove_neutrals = st.checkbox(label="Exclude neutrals from result")
    submitted = st.form_submit_button("Submit")

if submitted:
    # search
    data = scrape(keyword)
    # display the data
    st.dataframe(data)
    # truncate the post lengths before passing to the NLP pipline. max tokens: 514
    data["post"] = data["post"].str[:1500]
    try:
        res= get_sentiment(nlp, data["post"].tolist())
    except:
        st.error("Oops! Something went wrong 🚨. Try another keyword!")
    counts = count_sentiment(res)
    if remove_neutrals:
        del counts["neutral"]

    # display barplot
    fig = px.bar(x=list(counts.keys()), y=list(counts.values()), color=list(counts.keys()))

    def get_nnp(res):
        nnp=[]
        for (l,s) in res:
            if l == "positive": nnp.append(s)
            elif l == "negative": nnp.append(s*-1)
            else: nnp.append(0)
        return nnp

    nnp = get_nnp(res)

    data["sentiment"] = nnp

    # append scores to the dataframe

    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig, use_container_width=True)
    with c2:
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

        st.altair_chart(line+scatter, use_container_width=True)



