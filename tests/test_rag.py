from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate

from wtpdf.rag import (
    HARDENED_QA_PROMPT,
    QA_PROMPT,
    build_rag_chain,
    build_vectorstore,
    load_and_split,
)


def test_load_and_split_extracts_text(sample_pdf: Path) -> None:
    docs = load_and_split(str(sample_pdf))
    assert len(docs) == 1
    assert "Hello wtpdf test document." in docs[0].page_content
    assert docs[0].metadata["page"] == 0


def test_load_and_split_chunks_long_text(sample_pdf: Path) -> None:
    docs = load_and_split(str(sample_pdf))
    for doc in docs:
        assert len(doc.page_content) <= 1000


def test_build_vectorstore_returns_working_retriever() -> None:
    docs = [
        Document(page_content="The sky is blue.", metadata={"page": 0}),
        Document(page_content="Grass is green.", metadata={"page": 1}),
    ]
    embeddings = DeterministicFakeEmbedding(size=32)
    vectorstore = build_vectorstore(docs, embeddings)

    results = vectorstore.similarity_search("sky", k=1)
    assert len(results) == 1


def test_build_rag_chain_returns_answer_and_context() -> None:
    docs = [Document(page_content="wtpdf is a PDF Q&A demo.", metadata={"page": 0})]
    embeddings = DeterministicFakeEmbedding(size=32)
    vectorstore = build_vectorstore(docs, embeddings)
    retriever = vectorstore.as_retriever()

    chat_model = FakeListChatModel(responses=["This is a demo answer."])
    chain = build_rag_chain(chat_model, retriever)

    result = chain.invoke({"input": "What is wtpdf?"})

    assert result["answer"] == "This is a demo answer."
    assert result["context"]
    assert all(isinstance(doc, Document) for doc in result["context"])


def _rendered_messages(prompt: ChatPromptTemplate) -> list[tuple[str, str]]:
    messages = prompt.format_messages(context="DOC TEXT", input="QUESTION")
    return [(m.type, str(m.content)) for m in messages]


def test_vulnerable_prompt_puts_context_in_system_message() -> None:
    system, human = _rendered_messages(QA_PROMPT)
    assert "DOC TEXT" in system[1]
    assert "DOC TEXT" not in human[1]
    assert "WTPDF-STAFF-50" in system[1]


def test_hardened_prompt_delimits_context_in_human_message() -> None:
    system, human = _rendered_messages(HARDENED_QA_PROMPT)
    assert "DOC TEXT" not in system[1]
    assert "WTPDF-STAFF-50" in system[1]
    assert "<context>\nDOC TEXT\n</context>" in human[1]


def test_build_rag_chain_supports_hardened_mode() -> None:
    docs = [Document(page_content="wtpdf is a PDF Q&A demo.", metadata={"page": 0})]
    vectorstore = build_vectorstore(docs, DeterministicFakeEmbedding(size=32))
    chat_model = FakeListChatModel(responses=["ok"])
    chain = build_rag_chain(chat_model, vectorstore.as_retriever(), vulnerable=False)

    assert chain.invoke({"input": "What is wtpdf?"})["answer"] == "ok"
