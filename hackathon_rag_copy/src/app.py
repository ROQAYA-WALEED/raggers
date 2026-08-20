"""
app.py
------
Simple Streamlit chatbot UI for the RAG pipeline.
Talks directly to the retriever + generator (no need to run the FastAPI
server separately) — run with:

    streamlit run src/app.py
"""

import streamlit as st
from src.retrieval.retriever import retrieve, format_context
from src.generation.generator import generate_answer
from src.vectorstore.vector_store import vector_store

st.set_page_config(page_title="RAG Chatbot", page_icon="💬")
st.title("💬 RAG Chatbot")
st.caption(f"Knowledge base has {vector_store.count()} chunks loaded.")

# Keep the chat history in Streamlit's session state so it survives reruns
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": str}

# Replay previous messages on every rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom of the page
question = st.chat_input("Ask something about your documents...")

if question:
    # Show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Run the RAG pipeline: retrieve context -> ask Claude
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chunks = retrieve(question)
            context = format_context(chunks)
            answer = generate_answer(question, context)

            st.markdown(answer)

            # Show which chunks/sources were used, collapsed by default
            if chunks:
                with st.expander("Sources used"):
                    for i, chunk in enumerate(chunks, start=1):
                        st.markdown(f"**[{i}] {chunk['source']}**")
                        st.text(chunk["text"])

    st.session_state.messages.append({"role": "assistant", "content": answer})
