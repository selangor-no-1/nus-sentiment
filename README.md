# nus-sentiment

NUS Hack&amp;Roll 2023: Team 8 - Pink Mouse: NUS Sentiment

- Status: 🟩 **WIN** - **Coreteam's Best Roll** 
- Read More: [Devpost](https://devpost.com/software/nus-sentiment)

## Quick Start

```
git clone git@github.com:nus-sentiment/nus-sentiment.git
cd nus-sentiment
virtualenv venv
source venv/bin/activate
```

```
pip install -r requirements.txt
```

Run the entrypoint

```
streamlit run Search.py
```

## Credentials

In `/.streamlit/secrets.toml`

```
deta_key = "<deta.sh key>"
SECRET_KEY = "<reddit secrets key>"
ACCESS_TOKEN = "<reddit access token>"
PINECONE_KEY = "<pinecone api key>
USERNAME = "<reddit username>"
PASSWORD = "<reddit password>"
```

You can choose to omit `USERNAME` and `PASSWORD`. If you choose to do so remove these attributes from the `PRAW` Reddit object in `utils/reddit.py`.

## Powered By
<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Reddit_logo_new.svg/487px-Reddit_logo_new.svg.png?20220313085316" alt="reddit" width="100"/> 
  <br />
  <br />
  <img src="https://d33wubrfki0l68.cloudfront.net/682006698903a55560c796b901fdfe4446c6d27a/a00ee/images/pinecone-logo.svg" alt="pinecone" width="150" />   
  <br />
  <br />
  <img src="https://www.deta.sh/dist/images/deta_logo.svg" alt="deta" width="150" />  
  <br />
  <br />
  <img src="https://streamlit.io/images/brand/streamlit-mark-color.svg" alt="streamlit" width="100" /> 
</div>


