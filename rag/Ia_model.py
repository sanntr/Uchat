import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Configurar ruta al archivo .env en la raíz del proyecto
def get_ia_model():
    BASE_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(dotenv_path=BASE_DIR / ".env")

    api_key = os.getenv("API_KEY")
    
    return ChatGoogleGenerativeAI(model="gemini-3.5-flash", api_key=api_key)

