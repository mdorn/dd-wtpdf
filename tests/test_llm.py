import pytest
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from wtpdf.llm import OLLAMA, OPENAI, get_chat_model, get_embeddings


def test_get_chat_model_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    model = get_chat_model(OPENAI, "gpt-4o-mini")
    assert isinstance(model, ChatOpenAI)
    assert model.model_name == "gpt-4o-mini"


def test_get_chat_model_openai_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(KeyError):
        get_chat_model(OPENAI, "gpt-4o-mini")


def test_get_chat_model_ollama_default_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    model = get_chat_model(OLLAMA, "llama3.1")
    assert isinstance(model, ChatOllama)
    assert model.model == "llama3.1"
    assert model.base_url == "http://localhost:11434"


def test_get_chat_model_ollama_custom_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "http://example.com:1234")
    model = get_chat_model(OLLAMA, "llama3.1")
    assert model.base_url == "http://example.com:1234"


def test_get_chat_model_unknown_backend() -> None:
    with pytest.raises(ValueError, match="Unknown backend"):
        get_chat_model("bogus", "some-model")


def test_get_embeddings_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    embeddings = get_embeddings(OPENAI)
    assert isinstance(embeddings, OpenAIEmbeddings)
    assert embeddings.model == "text-embedding-3-small"


def test_get_embeddings_openai_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(KeyError):
        get_embeddings(OPENAI)


def test_get_embeddings_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    embeddings = get_embeddings(OLLAMA)
    assert isinstance(embeddings, OllamaEmbeddings)
    assert embeddings.model == "nomic-embed-text"
    assert embeddings.base_url == "http://localhost:11434"


def test_get_embeddings_unknown_backend() -> None:
    with pytest.raises(ValueError, match="Unknown backend"):
        get_embeddings("bogus")
