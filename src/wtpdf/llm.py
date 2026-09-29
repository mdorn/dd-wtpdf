import os

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

OPENAI = "OpenAI"
OLLAMA = "Ollama"

DEFAULT_MODELS = {
    OPENAI: "gpt-4o-mini",
    OLLAMA: "llama3.1",
    # OLLAMA: "gemma4:26b",
}

DEFAULT_EMBEDDING_MODELS = {
    OPENAI: "text-embedding-3-small",
    OLLAMA: "nomic-embed-text",
}


def get_chat_model(backend: str, model: str) -> BaseChatModel:
    if backend == OPENAI:
        return ChatOpenAI(model=model, api_key=os.environ["OPENAI_API_KEY"])
    if backend == OLLAMA:
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url)
    raise ValueError(f"Unknown backend: {backend}")


def get_embeddings(backend: str) -> Embeddings:
    if backend == OPENAI:
        return OpenAIEmbeddings(
            model=DEFAULT_EMBEDDING_MODELS[OPENAI],
            api_key=os.environ["OPENAI_API_KEY"],
        )
    if backend == OLLAMA:
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        return OllamaEmbeddings(
            model=DEFAULT_EMBEDDING_MODELS[OLLAMA], base_url=base_url
        )
    raise ValueError(f"Unknown backend: {backend}")
