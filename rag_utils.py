from langchain.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma, FAISS
from pathlib import Path


def load_documents_from_folder(folder_path: str):
    docs = []
    for pdf_path in Path(folder_path).glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_path))
        docs.extend(loader.load())
    return docs


def create_vectorstore(documents, persist_path: str = "./vectorstore"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma.from_documents(chunks, embedding, persist_directory=persist_path)
    db.persist()
    return db


def load_vectorstore(persist_path: str = "./vectorstore"):
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory=persist_path, embedding_function=embedding)


def load_uploaded_documents(files) -> list:
    all_docs = []
    for file in files:
        loader = UnstructuredPDFLoader(file_path=file.name, file=file)
        docs = loader.load()
        all_docs.extend(docs)
    return all_docs


def create_temp_vectorstore(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embedding)
