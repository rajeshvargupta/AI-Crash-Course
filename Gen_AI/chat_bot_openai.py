import streamlit as st
from openai import OpenAI
from streamlit_chat import message

# Initialize Client
client = OpenAI(api_key="")

st.title("ChatGPT ChatBot With Streamlit (Updated API)")

# Session State
if "user_messages" not in st.session_state:
    st.session_state["user_messages"] = []

if "bot_messages" not in st.session_state:
    st.session_state["bot_messages"] = []

# Function to call OpenAI
def api_calling(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # fast & cheap model
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Input box
def get_text():
    return st.text_input("Write here...", key="input")

user_input = get_text()

# When user sends message
if user_input:
    bot_reply = api_calling(user_input)

    # Save messages in session
    st.session_state.user_messages.append(user_input)
    st.session_state.bot_messages.append(bot_reply)

# Display chat history
if st.session_state["user_messages"]:
    for i in range(len(st.session_state["user_messages"])):
        # Show user message
        message(
            st.session_state["user_messages"][i],
            is_user=True,
            key=f"user_{i}"
        )
        # Show bot message
        message(
            st.session_state["bot_messages"][i],
            key=f"bot_{i}"
        )
