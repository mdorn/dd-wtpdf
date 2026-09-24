# wtpdf

A small Streamlit demo: upload a PDF and ask an LLM questions about it, backed by
LangChain retrieval (RAG) over an in-memory ChromaDB vector store.

Supports two LLM backends, selectable in the sidebar:
- **OpenAI** (requires an API key)
- **Ollama** (local, requires a running Ollama server)

## Setup

```
uv sync
```

For the OpenAI backend, export an API key:

```
export OPENAI_API_KEY=sk-...
```

For the Ollama backend, make sure Ollama is running locally and pull a chat and
an embedding model:

```
ollama serve
ollama pull llama3.1
ollama pull nomic-embed-text
```

By default the app connects to Ollama at `http://localhost:11434`. Override with:

```
export OLLAMA_HOST=http://localhost:11434
```

## Run

```
uv run streamlit run src/wtpdf/app.py
```

or

```
uv run wtpdf
```

Then open the URL Streamlit prints (usually http://localhost:8501), pick a
backend in the sidebar, upload a PDF, and start asking questions.
