import streamlit as st
import requests

# Your FastAPI backend URL
# BACKEND_URL = "http://localhost:8000/query"  # Change this if hosted elsewhere
BACKEND_URL = "https://ssaa-chatbot-backend-a3gxbhe2apa3ggg9.australiaeast-01.azurewebsites.net/query"
st.title("SSAA Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call backend API and get the response
    def get_response():
        try:
            response = requests.post(BACKEND_URL, json={"query": prompt})
            response_json = response.json()
            # Extract the answer from the response
            return response_json.get("answer", "No answer received.")
        except Exception as e:
            return f"Error: {e}"

    # Get the chatbot's response and add it to the messages
    response_content = get_response()

    # Display the assistant's response
    with st.chat_message("assistant"):
        st.markdown(response_content)
    st.session_state.messages.append({"role": "assistant", "content": response_content})
