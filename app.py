# app.py
import os
import streamlit as st
from dotenv import load_dotenv

# Import Aniket's backend function
from backend.vector_store import initialize_github_vector_store
# Import Jayraj's AI generation chain
from frontend.llm_chain import generate_rag_response

# Load secret API keys from local .env file
load_dotenv()

st.set_page_config(page_title="GitHub Code Chatter", page_icon="💻", layout="wide")
st.title("💻 GitHub Repository Code Chatter")
st.caption("Chat with any public GitHub repository using RAG & AST parsing")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Gemini API Key Security Toggle
    use_custom_key = st.toggle("Use Custom Gemini API Key")
    if use_custom_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    else:
        api_key = os.getenv("GOOGLE_API_KEY")
        st.caption("🔒 Using default developer `.env` key.")

    st.divider()
    
    repo_url = st.text_input("Public GitHub Repo URL:", placeholder="https://github.com/user/repository")
    index_btn = st.button("Index Repository")

    if index_btn:
        if not repo_url:
            st.warning("Please enter a GitHub repository URL.")
        elif not api_key:
            st.error("Missing Gemini API Key! Add it to .env or toggle custom key.")
        else:
            with st.spinner("Cloning and indexing repository..."):
                try:
                    # Call Aniket's backend function
                    st.session_state.retriever = initialize_github_vector_store(repo_url)
                    st.session_state.messages = [] # Reset chat for new repo
                    st.success("Repository indexed successfully!")
                except Exception as e:
                    st.error(f"Failed to index repository: {e}")

# --- MAIN CHAT INTERFACE ---
if "retriever" not in st.session_state or st.session_state.retriever is None:
    st.info("👈 Enter a public GitHub repository URL in the sidebar to start chatting.")
else:
    # Display previous messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if user_query := st.chat_input("Ask a question about this codebase..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate Gemini Response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing code chunks & generating response..."):
                try:
                    response_text = generate_rag_response(
                        retriever=st.session_state.retriever,
                        query=user_query,
                        api_key=api_key
                    )
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Error generating answer: {e}")