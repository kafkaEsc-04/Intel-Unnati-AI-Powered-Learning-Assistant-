from rag_utils import load_documents_from_folder, create_vectorstore

docs = load_documents_from_folder("pdfs")   # folder where PDFs are stored
print(f"Loaded {len(docs)} documents.")

create_vectorstore(docs)
print("Vector store created and persisted to disk.")
