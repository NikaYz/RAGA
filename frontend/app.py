# frontend/app.py
import streamlit as st
import requests

API_URL = "http://rag-backend:8000/query"

st.set_page_config(page_title="RAG Chat", page_icon="🤖", layout="centered")

st.title("📚 Julius Caesar Querer")

query = st.text_area("Ask your question:", placeholder="e.g. Who swayed Brutus?")
if st.button("Submit Query"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"query": query})
                response.raise_for_status()
                data = response.json()
                
                st.subheader("🧠 Epaphroditos's Answer:")
                st.write(data["answer"])
                
                st.markdown("---")
                st.subheader("📚 Sources:")
                for src in data["sources"]:
                    st.markdown(f"**Chunk:** {src}")
                    # st.json(src["metadata"])
                    st.markdown("---")
            except Exception as e:
                st.error(f"Error: {e}")
