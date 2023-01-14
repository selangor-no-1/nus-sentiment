import streamlit as st

def display_post(dict: dict):
    for k,v in dict.items():
        a, b = st.columns([1,4])
        a.write(f"**{k}**")
        b.write(v)

# takes in a list of dictionaries representating each post
# eg : [{},{},{}]
def display_all_posts(data):
    for post in data:
        display_post(post)
        st.markdown("---")

def paginator(
    data: list,
    page_size: int
) -> list:

    total_pages = -(-len(data) // page_size)

    if total_pages > 1:
        selected_page = st.selectbox(
            label="Select page",
            options=range(1, total_pages+1),
        )
    else:
        selected_page=1

    page_start = (selected_page-1) * page_size
    page_end = page_start + page_size

    return data[page_start:page_end]
