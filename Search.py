import streamlit as st
import pandas as pd
import transformers
import re
import praw
from utils.reddit import reddit_agent
from utils.helpers import more_than_two_codes 
from components.post_card import display_all_posts
from components.charts import bar, line_and_scatter, wordcloudchart
from utils.model import download_model, LABELS
from datetime import datetime

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
            if isValidComment(comment):
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
    
    # The parameters for tokenizer in nlp pipeline:
    tokenizer_kwargs = {'padding': True, 'truncation': True, 'max_length': 512}

    # Removing module codes from posts, since nlp won't know what they are
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

st.markdown("<h1>NUS Sentiment</h1>", unsafe_allow_html=True)
st.subheader("Scrape posts from r/NUS")

with st.form("scraper"):

    keyword = st.text_input(label="Input the keyword you wish to search for", placeholder="CS1010S")
    remove_neutrals = st.checkbox(label="Exclude neutrals from result")
    submitted = st.form_submit_button("Submit")

if submitted:
    # search
    data = scrape(keyword.lower())

    # Check if is Module
    module = re.search("(([A-Za-z]){2,3}\d{4}([A-Za-z]){0,1})", keyword)
    if module:
        col1, col2 = st.columns([.5,1])
        with col1:
            st.write("MODULE " + module.group(0).upper() + " DETECTED!!!")
        
        with col2:
            st.markdown(f'''<a href={"https://www.nusmods.com/modules/" + module.group(0)}>
                        <button style="background-color:#EF7C00;">NUSMODS</button></a>''',
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
    data["sentiment"] = nnp

    # display the data
    # st.dataframe(data) uncomment this time for debugging
    
    with st.expander("View posts"):
        display_all_posts(data)

    c1,c2 = st.columns(2)
    with c1:
        fig = bar(counts=counts)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        line_fig = line_and_scatter(data=data, keyword=keyword)
        st.altair_chart(line_fig, use_container_width=True)
    
    c3,c4 = st.columns(2)
    with c3:
        fig = wordcloudchart(data)
        st.pyplot(fig)

