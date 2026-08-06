# frontend/app.py
import streamlit as st
import sys
import os

# Adjust paths to import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.vector_store import initialize_github_vector_store

st.set_page_config(page_title="GitHub Code Chatter", layout="wide")
st.title("🤖 GitHub Repository Code Chatter")

# Initialize session state for storing retriever and chat history
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for repository ingestion
with st.sidebar:
    st.header("1. Ingest Repository")
    repo_url = st.text_input("Enter Public GitHub URL:")
    if st.button("Process Repository"):
        if repo_url:
            with st.spinner("Cloning and indexing repository..."):
                try:
                    # This will call the mock for now, and the real backend later
                    st.session_state.retriever = initialize_github_vector_store(repo_url)
                    st.success("Repository successfully indexed!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a URL.")

# Main chat interface
st.header("2. Chat with Codebase")
if st.session_state.retriever is None:
    st.info("Please enter a GitHub repository URL in the sidebar to get started.")
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if user_query := st.chat_input("Ask a question about the code..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Retrieve relevant code snippets
        retrieved_docs = st.session_state.retriever.get_relevant_documents(user_query)
        
        # Format a temporary response using retrieved snippets to test display
        response_text = "Here are the relevant code blocks I found:\n\n"
        for doc in retrieved_docs:
            response_text += f"**File:** `{doc.metadata['source']}`\n"
            response_text += f"```{doc.metadata['language']}\n{doc.page_content}\n```\n\n"
        response_text += "*(LLM integration will generate the actual synthesis here later)*"

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})