import streamlit as st
import pinecone
from utils.semantics import download_sentence_embedder
from components.post_card import display_post, paginator

# init pinecone session
pinecone.init(
    api_key=st.secrets["PINECONE_KEY"],
    environment="us-west1-gcp"
)

# init retriever
retriever = download_sentence_embedder()

index_name = "nus-sentiment" ## replace later

# check if the sentiment-mining index exists
if index_name not in pinecone.list_indexes():
    # create the index if it does not exist
    pinecone.create_index(
        index_name,
        dimension=384,
        metric="cosine"
    )

index = pinecone.Index(index_name)

##############################################################################################
### UI Start
##############################################################################################

st.markdown("<h1>Semantic Search</h1>", unsafe_allow_html=True)

with st.form("Semantic Search [Fast!]"):
    query = st.text_input(label="Input your query here")
    top_k_matches = st.number_input(label="Return the top K matches", min_value=1, max_value=500, value=1)
    submitted = st.form_submit_button("Submit")

    if not query:
        st.stop()

# generate dense vector embeddings for the query
xq = retriever.encode(query).tolist()
# query pinecone
result = index.query(xq, top_k=top_k_matches, include_metadata=True)

matches = result["matches"]
meta = [post["metadata"] for post in matches]

with st.expander("View matches"):
    for post in paginator(meta, 5):
        display_post(post)