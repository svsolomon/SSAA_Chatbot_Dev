import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FastAPI backend endpoint
BACKEND_URL = "http://localhost:8000/query"  # Change this to deployed URL in production

# Azure Blob base URL for document linking
AZURE_BLOB_BASE_URL = os.getenv("AZURE_BLOB_BASE_URL")

# Streamlit app title
st.title("SSAA Chatbot")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all past chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "docs" in message:
            # Build clickable document links
            doc_links = "<br>".join(
                f'<a href="{AZURE_BLOB_BASE_URL}{doc}" target="_blank">{doc}</a>'
                for doc in message["docs"]
            ) if message["docs"] else "No documents referenced."

            # Show disclaimer if flagged as insurance/liability-related
            disclaimer = (
                "<br><br><i><b>Disclaimer:</b> This response may not be sufficient to make an informed decision. "
                "Please consult a human agent for further assistance.</i>"
                if message.get("status") == '1' else ""
            )

            # Display assistant response with references
            full_response = f"{message['content']}<br><br><b>Referenced Documents:</b><br>{doc_links}{disclaimer}"
            st.markdown(full_response, unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

# User input prompt field
prompt = st.chat_input("Say something")
if prompt:
    # Display and store user's message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    def get_response():
        """
        Sends the user query to the backend and retrieves the answer, documents, and status.

        Returns:
            tuple: (answer str, list of documents, status flag)
        """
        try:
            response = requests.post(BACKEND_URL, json={"query": prompt})
            response_json = response.json()
            answer = response_json.get("answer", "No answer received.")
            documents = response_json.get("documents", [])
            status = response_json.get("status", None)
            return answer, documents, status
        except Exception as e:
            return f"Error: {e}", [], None

    # Fetch answer from backend
    response_content, referenced_docs, status = get_response()

    # Display assistant response
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
            # Build document reference links
            doc_links = "<br>".join(
                f'<a href="{AZURE_BLOB_BASE_URL}{doc}" target="_blank">{doc}</a>'
                for doc in referenced_docs
            ) if referenced_docs else "No documents referenced."

            # Add disclaimer for sensitive topics
            disclaimer = (
                "<br><br><i><b>Disclaimer:</b> This response may not be sufficient to make an informed decision. "
                "Please consult a human agent for further assistance.</i>"
                if status == '1' else ""
            )

            # Combine response, documents, and disclaimer
            full_response = f"{response_content}<br><br><b>Referenced Documents:</b><br>{doc_links}{disclaimer}"
            st.markdown(full_response, unsafe_allow_html=True)

            # Store assistant's message in session
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_content,
                "docs": referenced_docs,
                "status": status
            })
