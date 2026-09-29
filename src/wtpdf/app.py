import logging
import os
import tempfile
import uuid

import streamlit as st

from wtpdf.llm import DEFAULT_MODELS, OLLAMA, OPENAI, get_chat_model, get_embeddings
from wtpdf.rag import build_rag_chain, build_vectorstore, load_and_split

logger = logging.getLogger(__name__)

GENERIC_ERROR = "Something went wrong. Please try again."

st.set_page_config(page_title="wtpdf - PDF Q&A", page_icon="📄")
st.title("📄 wtpdf: Ask questions about a PDF")

with st.sidebar:
    st.header("Settings")
    backend = st.selectbox("LLM backend", [OPENAI, OLLAMA])
    model = st.text_input("Model", value=DEFAULT_MODELS[backend])
    vulnerable = st.checkbox(
        "Vulnerable mode (OWASP demo)",
        value=True,
        help="Intentionally unsafe: PDF text is treated as system instructions "
        "(LLM01), all sessions share one vector store, PII is not redacted and "
        "raw errors are shown (LLM02). Uncheck to use the hardened behavior.",
    )

    if backend == OPENAI and not os.environ.get("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set in the environment.")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

index_key = (uploaded_file.name if uploaded_file else None, backend, vulnerable)
if uploaded_file is not None and st.session_state.get("index_key") != index_key:
    if backend == OPENAI and not os.environ.get("OPENAI_API_KEY"):
        st.stop()

    with st.spinner("Indexing document..."):
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp.flush()
                docs = load_and_split(tmp.name, redact=not vulnerable)

            embeddings = get_embeddings(backend)
            collection_name = None
            if not vulnerable:
                collection_name = f"wtpdf-{uuid.uuid4()}"
            vectorstore = build_vectorstore(docs, embeddings, collection_name)
            st.session_state.retriever = vectorstore.as_retriever()
            st.session_state.index_key = index_key
            st.session_state.messages = []
        except Exception as exc:
            if vulnerable:
                st.error(f"Failed to index document: {exc}")
            else:
                logger.exception("Failed to index document")
                st.error(GENERIC_ERROR)
            st.stop()

    st.success(f"Indexed {len(docs)} chunks from {uploaded_file.name}.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.get("retriever") is None:
    st.info("Upload a PDF to start asking questions.")
else:
    question = st.chat_input("Ask a question about the document")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                chat_model = get_chat_model(backend, model)
                chain = build_rag_chain(
                    chat_model, st.session_state.retriever, vulnerable=vulnerable
                )
                result = chain.invoke({"input": question})
                answer = result["answer"]
                st.markdown(answer)

                sources = result.get("context", [])
                if sources:
                    with st.expander("Sources"):
                        for doc in sources:
                            page = doc.metadata.get("page")
                            st.markdown(f"**Page {page}**\n\n{doc.page_content}")
            except Exception as exc:
                if vulnerable:
                    answer = f"Error: {exc}"
                else:
                    logger.exception("Failed to answer question")
                    answer = GENERIC_ERROR
                st.error(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
