import streamlit as st
import pandas as pd
import transformers
import re
import praw
from utils.reddit import reddit_agent
from utils.helpers import more_than_two_codes 
from components.post_card import display_post, paginator
from components.charts import bar, line_and_scatter, wordcloudchart
from utils.model import download_model, LABELS
from datetime import datetime

st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_icon="📈")

# instantiate reddit agent
reddit = reddit_agent()
nus_sub = reddit.subreddit("nus")

# instatntiate model
_, tokenizer, nlp  = download_model()

####################################################################################################
# Data Functions
####################################################################################################

# collection of bools to check whether we want to include a post or not
def isValidComment(comment):
    return (not isinstance(comment, praw.models.MoreComments)) \
        and (comment.author != "AutoModerator") \
        and (comment.body != "[deleted]") \
        and (not more_than_two_codes(comment.body))


@st.experimental_memo(ttl=60*60)
def scrape(keyword: str, start_date: datetime, end_date: datetime):
    data = []

    for post in nus_sub.search(keyword):
        comments = post.comments
        comments_list = comments.list()

        # add the body of the post itself
        data.append((post.title, post.author, datetime.fromtimestamp(post.created_utc), post.selftext, post.url))

        # BFS
        while len(comments_list) > 0:
            comment = comments_list.pop(0)
            if isValidComment(comment):
                data.append((post.title, comment.author, datetime.fromtimestamp(comment.created_utc), comment.body, post.url))
            elif isinstance(comment, praw.models.MoreComments):
                comments_list.extend(comment.comments())
    
    df = pd.DataFrame(data, columns=["thread_title", "author", "created_at", "post", "url"])
    return df[df["created_at"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))]


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
    
    # The parameters for tokenizer in nlp pipeline:
    tokenizer_kwargs = {"padding": True, "truncation": True, "max_length": 512}

    # Removing module codes from posts, since nlp won"t know what they are
    removeCodes = []
    for post in posts:
        removeCodes.append(re.sub("(([A-Za-z]){2,3}\d{4}([A-Za-z]){0,1})", "", post))

    sentiments = nlp(removeCodes, **tokenizer_kwargs)

    l = [LABELS[x["label"]] for x in sentiments]
    s = [x["score"] for x in sentiments]

    return list(zip(l,s))

def count_sentiment(result):
    sentiments = {"negative": 0, "neutral": 0, "positive": 0}
    for sentiment, _ in result:
        sentiments[sentiment] += 1
    return sentiments

####################################################################################################
# Begin UI
####################################################################################################

hide_streamlit_style = """
            <style>
            code, h1 {color: #ff5138;}
            h3, p {color: #fff;}
            footer {visibility: hidden;}
            input {color: #fff !important;}
            button:hover {background-color: #ff5138;}
            button:focus {box-shadow: #ff5138;}
            </style>
            <h1>NUS Sentiment</h1>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
st.subheader("Scrape posts from r/NUS")

with st.form("scraper"):

    keyword = st.text_input(label="Input the keyword you wish to search for", placeholder="CS1010S")
    remove_neutrals = st.checkbox(label="Exclude neutrals from result")

    # columns for date selectors
    tc1, tc2 = st.columns(2)
    with tc1:
        start_date = st.date_input("Start date", datetime.fromisoformat("2015-01-01"))
    with tc2:
        end_date = st.date_input("End date", datetime.now())

    if start_date >= end_date:
        st.error("Error: End date must be after start date.")

    submitted = st.form_submit_button("Submit")

    if not keyword:
        st.stop()

data = scrape(keyword.lower(), start_date, end_date)


# Check if is Module
module = re.search("(([A-Za-z]){2,3}\d{4}([A-Za-z]){0,1})", keyword)
if module:
    col1, col2 = st.columns([.5,1])
    with col1:
        st.markdown(f"Module **{module.group(0).upper()}** detected!. Head to")
    with col2:
        st.markdown(f'''<a href={"https://www.nusmods.com/modules/" + module.group(0)}>
                    <img src="https://raw.githubusercontent.com/nusmodifications/nusmods/1160b6f080a734cb51a5cc2878d0a5cb3ebf3b6b/misc/nusmods-logo.svg" alt="nusmods-svg" width="100"/></a>''',
                    unsafe_allow_html=True)

# truncate the post lengths before passing to the NLP pipline. max tokens: 514
data["post"] = data["post"].str[:1500]

res = get_sentiment(nlp, data["post"].tolist())

counts = count_sentiment(res)
if remove_neutrals:
    del counts["neutral"]

nnp = []
for l, s in res:
    if l == "positive":
        nnp.append(s)
    elif l == "negative":
        nnp.append(-s)
    else:
        nnp.append(0)

# append scores to the dataframe
data.insert(loc=1, column="sentiment", value=nnp)

posts = list(data.to_dict(orient="records"))

# display the data in expander
with st.expander("View posts"):
    opts_time = ["Old to New", "New to Old"]
    opts_sent = ["High to Low", "Low to High"]
    c1,c2 = st.columns(2)
    with c1:
        time = st.selectbox(label="Sort by created time", options=opts_time)
    with c2:
        sentiment = st.selectbox(label="Sort by sentiment", options=opts_sent)

    if time == opts_time[0]:
        posts.sort(key=lambda x: x["created_at"], reverse=False)
    else:
        posts.sort(key=lambda x: x["created_at"], reverse=True)

    if sentiment == opts_sent[0]:
        posts.sort(key=lambda x: x["sentiment"], reverse=True)
    else:
        posts.sort(key=lambda x: x["sentiment"], reverse=False)

    for post in paginator(posts, 5):
        display_post(post)


fig = bar(counts=counts)
c1,c2 = st.columns(2)

with c1:

    st.markdown('')
    st.markdown('')
    st.markdown("**Summary Statistics:**")
    st.markdown(':green[Positive Posts:] ' + str(counts['positive']))
    st.markdown('Neutrual Posts: ' + str(counts['neutral']))
    st.markdown(':red[Negative Posts:] ' + str(counts['negative']))
    st.markdown("Total Posts: " + str(counts['positive'] + counts['negative'] + counts['neutral']))
    sentiment_float = data['sentiment'].mean()
    st.markdown("Average Sentiment: " + str(float(f'{sentiment_float:.3f}')))
    
    
with c2:

    st.plotly_chart(fig, use_container_width=True)


st.info("Use CTRL + CLICK on the points to open the Reddit thread in a new tab!",icon="ℹ️")

line_fig = line_and_scatter(data=data, keyword=keyword)
st.altair_chart(line_fig, use_container_width=True)


fig = wordcloudchart(data)
c3,c4,c5 = st.columns(3)

with c3:
    st.pyplot(fig[0])
with c4:
    st.pyplot(fig[1])
with c5:
    st.pyplot(fig[2])
