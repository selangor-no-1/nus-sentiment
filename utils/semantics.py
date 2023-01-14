import dateutil.parser
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer
from stqdm import stqdm


@st.experimental_singleton
def download_sentence_embedder():
    retriever = SentenceTransformer(
        'sentence-transformers/all-MiniLM-L6-v2'
    )
    return retriever
