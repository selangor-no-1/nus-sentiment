from typing import List

def post_card(
    title: str,
    posts: List[str]
):

    p_template = lambda post: f"""
    <p class="card-text">{post}</p>
    """

    all_posts_content = [p_template(post) for post in posts]

    return f"""
    <div class="card text-center">
        <div class="card-body">
            <h5 class="card-title mb-1 font-weight-bold">{title}</h5>
            <p class="card-text">{all_posts_content}</p>
        </div>
    </div>
    """