import streamlit as st
from openai import OpenAI
from inference import generate_answer

st.title("SSAA Chatbot")

client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

# message = role + content
# {role: user, content: hi}
# {role: assistant, content: Hi! I am a chatbot.}

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role":"user","content": prompt})

    # response = client.chat.completions.create(
    #     model = "gpt-3.5-turbo",
    #     messages = st.session_state.messages
    # ).choices[0].message.content
    stream = generate_answer(prompt)
    response = st.write_stream(stream)
    st.session_state.messages.append({"role":"assistant","content":response})