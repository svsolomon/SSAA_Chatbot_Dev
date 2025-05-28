import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your FastAPI backend URL
BACKEND_URL = "http://localhost:8000/query"  # Update if hosted elsewhere

# Azure Blob base URL from .env
AZURE_BLOB_BASE_URL = os.getenv("AZURE_BLOB_BASE_URL")

# App title
st.title("SSAA Chatbot")

# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "docs" in message:
            # Rebuild HTML with safe rendering
            doc_links = "<br>".join(
                f'<a href="{AZURE_BLOB_BASE_URL}{doc}" target="_blank">{doc}</a>'
                for doc in message["docs"]
            ) if message["docs"] else "No documents referenced."

            # Add disclaimer if status is '1'
            disclaimer = (
                "<br><br><i><b>Disclaimer:</b> This response may not be sufficient to make an informed decision. "
                "Please consult a human agent for further assistance.</i>"
                if message.get("status") == '1' else ""
            )

            full_response = f"{message['content']}<br><br><b>Referenced Documents:</b><br>{doc_links}{disclaimer}"
            st.markdown(full_response, unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

# User prompt input
prompt = st.chat_input("Say something")
if prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Backend API call
    def get_response():
        try:
            response = requests.post(BACKEND_URL, json={"query": prompt})
            response_json = response.json()
            answer = response_json.get("answer", "No answer received.")
            documents = response_json.get("documents", [])
            status = response_json.get("status", None)
            return answer, documents, status
        except Exception as e:
            return f"Error: {e}", [], None

    # Get chatbot reply and documents
    response_content, referenced_docs, status = get_response()

    # Format assistant reply
    with st.chat_message("assistant"):
        if response_content.startswith("Error:"):
            st.markdown(response_content)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_content,
                "docs": [],
                "status": None
            })
        else:
            doc_links = "<br>".join(
                f'<a href="{AZURE_BLOB_BASE_URL}{doc}" target="_blank">{doc}</a>'
                for doc in referenced_docs
            ) if referenced_docs else "No documents referenced."

            disclaimer = (
                "<br><br><i><b>Disclaimer:</b> This response may not be sufficient to make an informed decision. "
                "Please consult a human agent for further assistance.</i>"
                if status == '1' else ""
            )

            full_response = f"{response_content}<br><br><b>Referenced Documents:</b><br>{doc_links}{disclaimer}"
            st.markdown(full_response, unsafe_allow_html=True)

            # Save message with status
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_content,
                "docs": referenced_docs,
                "status": status
            })
