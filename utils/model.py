import streamlit as st
import torch
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification
)

MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment"

LABELS = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}

@st.experimental_singleton
def download_model(model_id: str = MODEL_ID):
    device = torch.cuda.current_device() if torch.cuda.is_available() else None

    model = AutoModelForSequenceClassification.from_pretrained(
        model_id,
        num_labels=3 # get positive, neutral, negative labels
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    nlp = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=device
    )
    return model, tokenizer, nlp