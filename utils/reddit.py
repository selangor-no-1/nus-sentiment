import praw
import streamlit as st


# instantiate reddit agent
def reddit_agent():
    
    client_id = st.secrets['ACCESS_TOKEN']
    client_secret = st.secrets['SECRET_KEY']
    username = st.secrets['USERNAME']
    password = st.secrets["PASSWORD"]
    user_agent = "dev"

    reddit = praw.Reddit(
        client_id = client_id,
        client_secret = client_secret,
        user_agent = user_agent,
        username= username,
        password= password
    )

    return reddit


