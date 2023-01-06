import streamlit as st
import streamlit.components.v1 as components
import random
import openai
import re
openai.api_key = "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"



def generate_text(topic: str, mood: str = ""):
    """Generate Tweet text."""
    if st.session_state.n_requests >= 5:
        st.session_state.text_error = "Too many requests. Please wait a few seconds before generating another Tweet."
        st.session_state.n_requests = 1
        return
    st.session_state.tweet = ""
    st.session_state.image = ""
    st.session_state.text_error = ""

    if not topic:
        st.session_state.text_error = "Please enter a topic"
        return

    with text_spinner_placeholder:
        with st.spinner("Please wait while your Tweet is being generated..."):
            mood_prompt = f"{mood} " if mood else ""
            kwargs = {
                "engine": "text-davinci-003",
                'prompt': f"Write a {mood_prompt}Tweet about {topic} in less than 120 characters:\n\n",
                "temperature": 0.7,
                "max_tokens": 256,
                "top_p": 1,  # default
                "frequency_penalty": 0,  # default
                "presence_penalty": 0,  # default
    }
            try:
                response = openai.Completion.create(**kwargs)
                st.session_state.tweet = response["choices"][0]["text"]
                return st.session_state.tweet

            except Exception as e:
                st.session_state.text_error = f"OpenAI API error: {e}"
 

def generate_image(prompt: str):
    """Generate Tweet image."""
    if st.session_state.n_requests >= 5:
        st.session_state.text_error = "Too many requests. Please wait a few seconds before generating another text or image."
        st.session_state.n_requests = 1
        return
    
    with image_spinner_placeholder:
        with st.spinner("Please wait while your image is being generated..."):
            prompt_wo_hashtags = re.sub("#[A-Za-z0-9_]+", "", prompt)
            processing_prompt = (
                "Create a detailed but brief description of an image that captures "
                f"the essence of the following text:\n{prompt_wo_hashtags}\n\n"
            )

        response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512",
                response_format="url",
                )
    st.session_state.image= response["data"][0]["url"]
    return st.session_state.image  
if "tweet" not in st.session_state:
    st.session_state.tweet = ""
if "image" not in st.session_state:
    st.session_state.image = ""
if "text_error" not in st.session_state:
    st.session_state.text_error = ""
if "image_error" not in st.session_state:
    st.session_state.image_error = ""
if "feeling_lucky" not in st.session_state:
    st.session_state.feeling_lucky = False
if "n_requests" not in st.session_state:
    st.session_state.n_requests = 0






# Render Streamlit page
st.title("Generate Tweets")
st.markdown(
    "This mini-app generates Tweets using OpenAI's GPT-3 based [Davinci model](https://beta.openai.com/docs/models/overview) for texts and [DALL·E](https://beta.openai.com/docs/guides/images) for images."
)

topic = st.text_input(label="Topic (or hashtag)", placeholder="AI")
mood = st.text_input(
    label="Mood (e.g. inspirational, funny, serious) (optional)",
    placeholder="inspirational",
)
col1, col2 = st.columns(2)
with col1:
    st.session_state.feeling_lucky = not st.button(
        label="Generate text",
        type="primary",
        on_click=generate_text,
        args=(topic, mood),
    )

with col2:
    with open("moods.txt") as f:
        sample_moods = f.read().splitlines()
    st.session_state.feeling_lucky = st.button(
        label="Feeling lucky",
        type="secondary",
        on_click=generate_text,
        args=("an interesting topic", random.choice(sample_moods)),
    )

text_spinner_placeholder = st.empty()
if st.session_state.text_error:
    st.error(st.session_state.text_error)


if st.session_state.tweet:
    st.markdown("""---""")
    st.text_area(label="Tweet", value=st.session_state.tweet, height=100)
    col1, col2 = st.columns(2)
    with col1:
        components.html(
            f"""
                <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-size="large" data-text="{st.session_state.tweet}\n - Tweet generated via" data-url="https://tweets.streamlit.app" data-show-count="false">Tweet</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            """,
            height=45,
        )
    with col2:
        st.button(
            label="Regenerate text",
            type="secondary",
            on_click=generate_text,
            args=(topic, mood),
        )
    if not st.session_state.image:
        st.button(
            label="Generate image",
            type="primary",
            on_click=generate_image,
            args=[st.session_state.tweet],
        )
    else:
        st.image(st.session_state.image)
        st.button(
            label="Regenerate image",
            type="secondary",
            on_click=generate_image,
            args=[st.session_state.tweet],
        )

    image_spinner_placeholder = st.empty()
    if st.session_state.image_error:
        st.error(st.session_state.image_error)
