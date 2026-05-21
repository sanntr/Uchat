from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from Ia_model import get_ia_model

# Cargar embeddings y base de datos FAISS una sola vez en memoria al iniciar el servicio web
embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2")
db = FAISS.load_local(
    "rag/vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

def querry_user(querry):
    # La búsqueda ahora es casi instantánea (milisegundos) porque la BD y el modelo están en memoria
    docs = db.similarity_search(querry, k=3)

    contexto = "\n".join([
        r.page_content
        for r in docs
    ])

    prompt = f"""
    Eres un asistente universitario.

    Usa SOLO esta información:

    {contexto}

    Pregunta:
    {querry}
    """
    model = get_ia_model()
    model_response = model.invoke(prompt)
    return model_response.content[0]["text"]

if __name__ == "__main__":
    print(querry_user("Que procesador tiene la pc de la biblioteca?"))
