from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from tempfile import TemporaryDirectory
from pathlib import Path
import os

BASE_VECTORSTORE_PATH = "./vectorstore"

def load_documents_from_folder(folder_path):
    docs = []
    folder = Path(folder_path)
    for file in folder.glob("*.pdf"):
        try:
            loader = PyPDFLoader(str(file))
            docs.extend(loader.load())
        except Exception:
            loader = UnstructuredPDFLoader(str(file))
            docs.extend(loader.load())
    return docs

def create_vectorstore_for_session(docs, session_id: str):
    persist_path = os.path.join(BASE_VECTORSTORE_PATH, session_id)
    os.makedirs(persist_path, exist_ok=True)

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
    db = Chroma.from_documents(chunks, embedding, persist_directory=persist_path)
    db.persist()
    return db

def load_vectorstore_for_session(session_id: str):
    persist_path = os.path.join(BASE_VECTORSTORE_PATH, session_id)
    if not os.path.exists(persist_path):
        return None
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory=persist_path, embedding_function=embedding)

def get_context_from_query(query: str, session_id: str, uploaded_files=None, threshold: float = 0.7) -> str:
    # Step 1: Handle uploaded files
    if uploaded_files:
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            for uploaded_file in uploaded_files:
                with open(temp_dir_path / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            docs = load_documents_from_folder(temp_dir_path)
            if not docs:
                return ""
            vectorstore = create_vectorstore_for_session(docs, session_id)
    else:
        vectorstore = load_vectorstore_for_session(session_id)
        if not vectorstore:
            return ""

    # Step 2: Similarity search with score
    try:
        results = vectorstore.similarity_search_with_score(query, k=5)
    except Exception:
        return ""

    relevant_chunks = [doc.page_content for doc, score in results if score >= threshold]
    return "\n".join(relevant_chunks) if relevant_chunks else ""
