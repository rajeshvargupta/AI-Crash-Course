import streamlit as st
import httpx

# --------------------------------------------------------
# HARD-CODED API KEY (unsafe but you requested it)
# --------------------------------------------------------
API_KEY = ""
MODEL_ID = "gemini-2.5-flash"

BASE_URL = "https://generativelanguage.googleapis.com"
GENERATE_ENDPOINT = f"/v1beta/models/{MODEL_ID}:generateContent"


# --------------------------------------------------------
# SAFE TEXT EXTRACTOR (works for all Gemini response formats)
# --------------------------------------------------------
def extract_gemini_text(data):
    """Safely extract text from any Gemini API format."""

    # candidates[0].text (new format)
    try:
        return data["candidates"][0]["text"]
    except:
        pass

    # candidates[0].content[].parts[].text (classic format)
    try:
        return data["candidates"][0]["content"][0]["parts"][0]["text"]
    except:
        pass

    # outputText
    if isinstance(data, dict) and "outputText" in data:
        return data["outputText"]

    # text
    if isinstance(data, dict) and "text" in data:
        return data["text"]

    return "⚠️ Unrecognized API response: " + str(data)


# --------------------------------------------------------
# GEMINI CHAT FUNCTION
# --------------------------------------------------------
def gemini_chat(user_msg):

    system_prompt = (
        "You are a safe medical assistant. "
        "Provide general information only. "
        "ALWAYS include this warning: 'This is not medical advice. Consult a doctor for accurate diagnosis.'"
    )

    # Build messages for Gemini
    contents = [
        {"role": "user", "parts": [{"text": system_prompt}]}  # system = user role for Gemini
    ]

    # Add conversation history
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"   # assistant → model
        contents.append({
            "role": role,
            "parts": [{"text": msg["text"]}]
        })

    # Add latest user message
    contents.append({
        "role": "user",
        "parts": [{"text": user_msg}]
    })

    payload = {
        "contents": contents,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}
    }

    headers = {"x-goog-api-key": API_KEY}

    # send request
    with httpx.Client(timeout=40.0) as client:
        response = client.post(
            BASE_URL + GENERATE_ENDPOINT,
            json=payload,
            headers=headers
        )

    data = response.json()
    return extract_gemini_text(data)


# --------------------------------------------------------
# STREAMLIT UI
# --------------------------------------------------------
st.set_page_config(page_title="Medicine Assistant", page_icon="💊")

st.title("💊 Medicine Assistant Chatbot")

st.write(
    "**Disclaimer:** This chatbot provides general medical information only. "
    "It is NOT a substitute for a certified doctor."
)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "text": "Hello! I can help with symptoms, medicines, and side effects."}
    ]

# Display messages
for msg in st.session_state.messages:
    st.chat_message("assistant" if msg["role"] == "model" else "user").write(msg["text"])

# Chat input
user_input = st.chat_input("Ask anything about symptoms, medicines, dosage...")

if user_input:
    # show user message
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "text": user_input})

    # bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = gemini_chat(user_input)
            st.write(reply)

    st.session_state.messages.append({"role": "model", "text": reply})
