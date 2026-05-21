from langchain_community.document_loaders import TextLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
def reader_txt(file_txt):
    file_path=Path(file_txt)
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    return docs


def vectorizer_txt(file_txt):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    chunks = text_splitter.split_documents(reader_txt(file_txt))

    embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2")

    db = FAISS.from_documents(
        chunks,
        embeddings
    )
    db.save_local("rag/vector_db")

if __name__ == "__main__":
    vectorizer_txt("rag/documents/universidad.txt")