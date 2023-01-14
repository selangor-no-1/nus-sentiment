import praw
import os
from dotenv import load_dotenv

# read .env
load_dotenv()

# instantiate reddit agent
def reddit_agent():
    
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

    return reddit


