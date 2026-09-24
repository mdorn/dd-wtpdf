from langchain_chroma import Chroma
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_text_splitters import RecursiveCharacterTextSplitter

SYSTEM_PROMPT = (
    "You are an assistant answering questions about an uploaded PDF. "
    "Use only the following retrieved context to answer the question. "
    "If you don't know the answer from the context, say so.\n\n{context}"
)

QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ]
)


def load_and_split(pdf_path: str) -> list[Document]:
    pages = PyPDFLoader(pdf_path).load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(pages)


def build_vectorstore(docs: list[Document], embeddings: Embeddings) -> Chroma:
    return Chroma.from_documents(docs, embedding=embeddings)


def build_rag_chain(chat_model: BaseChatModel, retriever: Runnable) -> Runnable:
    combine_docs_chain = create_stuff_documents_chain(chat_model, QA_PROMPT)
    return create_retrieval_chain(retriever, combine_docs_chain)
