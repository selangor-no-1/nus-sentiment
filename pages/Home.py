import streamlit as st
from utils.model import download_model, LABELS

model, tokenizer, nlp = download_model()

text = st.text_input(label="Input the text you want to analyse")
st.write(f"You inputted: \n {text}")

out = nlp(text)
label = out[0]["label"]
confidence = out[0]["score"]
st.write(LABELS[label], confidence)