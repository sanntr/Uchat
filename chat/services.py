import os
from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from google.genai import Client as GeminiClient
from google.genai import types



class ContextValidator:
    """Valida si una pregunta pertenece al ámbito universitario."""

    # ── Saludos y preguntas meta sobre el bot ──
    SALUDOS = [
        "hola", "buenos días", "buenas tardes", "buenas noches",
        "hey", "saludos", "qué tal", "hi", "hello",
    ]

    PREGUNTAS_META = [
        "qué puedes hacer", "qué haces", "cómo funciona",
        "ayuda", "help", "quién eres", "para qué sirves",
        "qué eres", "cómo me puedes ayudar",
    ]

    MENSAJE_BIENVENIDA = (
        "¡Hola! 👋 Soy el asistente virtual universitario. Puedo ayudarte con:\n\n"
        "• 📅 Horarios e inicio de clases\n"
        "• 📚 Materias, pensum y plan de estudio\n"
        "• 📝 Inscripciones y matrícula\n"
        "• 💰 Pagos y colegiatura\n"
        "• 📊 Notas y calificaciones\n"
        "• 🏫 Información de facultades y carreras\n"
        "• 🎓 Becas y financiamiento\n\n"
        "¡Pregúntame lo que necesites!"
    )

    PALABRAS_CLAVE = [
        # ── Calendario y clases ──
        "clase", "clases", "inicio de clases", "fin de clases",
        "calendario académico", "periodo académico", "ciclo",
        "horario", "semestre", "trimestre", "periodo",
        "calendario", "fecha", "cuándo",

        # ── Materias y pensum ──
        "materia", "curso", "asignatura", "pensum", "plan de estudio",
        "requisito", "pre-requisito", "correquisito", "crédito", "créditos",
        "electiva", "optativa", "obligatoria",

        # ── Evaluación ──
        "nota", "notas", "calificación", "examen", "evaluación",
        "promedio", "índice", "reprobado", "aprobado", "parcial", "final",
        "tarea", "taller", "práctico", "laboratorio", "trabajo",

        # ── Inscripción y trámites ──
        "inscripción", "matrícula", "preinscripción", "reinscripción",
        "admisión", "ingreso", "vacante", "cupo", "baja", "retiro",
        "registro", "control de estudio", "acta", "constancia",
        "certificado", "título", "grado",

        # ── Pagos ──
        "pago", "colegiatura", "arancel", "cuota", "factura",
        "beca", "financiamiento", "descuento",

        # ── Personas ──
        "docente", "profesor", "estudiante", "tutor",

        # ── Espacios y servicios ──
        "aula", "biblioteca", "laboratorio", "facultad", "decanato",
        "rectoría", "secretaría", "carrera", "universidad",
        "bienestar", "psicología", "consejería", "tutoría",
        "deporte", "cultura", "evento", "actividad",

        # ── Postgrado ──
        "postgrado", "maestría", "doctorado", "diplomado",
        "extensión", "investigación",

        # ── Horarios de atención ──
        "horario de atención", "atención",
    ]

    @classmethod
    def es_saludo_o_meta(cls, pregunta: str) -> bool:
        pregunta_lower = pregunta.lower().strip()
        todas = cls.SALUDOS + cls.PREGUNTAS_META
        return any(palabra in pregunta_lower for palabra in todas)

    @classmethod
    def es_pregunta_universitaria(cls, pregunta: str) -> bool:
        pregunta_lower = pregunta.lower()
        return any(palabra in pregunta_lower for palabra in cls.PALABRAS_CLAVE)

    @classmethod
    def obtener_mensaje_restriccion(cls) -> str:
        return (
            "Lo siento, solo puedo responder preguntas relacionadas con "
            "el ámbito universitario (horarios, materias, notas, pagos, "
            "inscripciones, etc.). Por favor, haz una pregunta académica."
        )


class RAGService:
    """Servicio singleton para búsqueda semántica en FAISS."""

    _embeddings = None
    _db = None

    @classmethod
    def _inicializar(cls):
        if cls._db is not None:
            return
        cls._embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2")
        vector_db_path = os.path.join(settings.BASE_DIR, "rag", "vector_db")
        cls._db = FAISS.load_local(
            vector_db_path,
            cls._embeddings,
            allow_dangerous_deserialization=True,
        )

    @classmethod
    def buscar(cls, query: str, k: int = 3) -> str:
        cls._inicializar()
        try:
            docs = cls._db.similarity_search(query, k=k)
            return "\n".join(doc.page_content for doc in docs)
        except Exception as e:
            raise RuntimeError(f"Error al buscar en FAISS: {e}")


class GeminiService:
    """Servicio singleton para comunicación directa con Gemini API (sin retries automáticos)."""

    _client = None
    MODELO = "gemini-3.5-flash"

    @classmethod
    def _inicializar(cls):
        if cls._client is not None:
            return
        load_dotenv(dotenv_path=settings.BASE_DIR / ".env")
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY no encontrada. Revisa tu archivo .env")
        cls._client = GeminiClient(api_key=api_key)

    @classmethod
    def generar_respuesta(cls, contexto: str, pregunta: str) -> str:
        cls._inicializar()
        prompt = (
            "Eres un asistente virtual especializado en temas universitarios.\n\n"
            "Usa SOLO la siguiente información para responder:\n\n"
            f"{contexto}\n\n"
            f"Pregunta del estudiante:\n{pregunta}\n\n"
            "Responde de manera clara, concisa y útil.\n"
            "Si la información no está disponible en el contexto, indícalo amablemente."
        )
        try:
            response = cls._client.models.generate_content(
                model=cls.MODELO,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                    temperature=0.3,
                ),
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error al generar respuesta con Gemini: {e}")



class ChatbotService:
    """Orquesta el flujo completo del chatbot."""

    def procesar_pregunta(self, pregunta: str) -> dict:
        if not pregunta or not pregunta.strip():
            return {"respuesta": "Por favor, escribe una pregunta.", "valida": False}

        # ── 1. Saludos y preguntas sobre el bot → respuesta directa ──
        if ContextValidator.es_saludo_o_meta(pregunta):
            return {
                "respuesta": ContextValidator.MENSAJE_BIENVENIDA,
                "valida": True,
            }

        # ── 2. Validación de contexto universitario ──
        if not ContextValidator.es_pregunta_universitaria(pregunta):
            return {
                "respuesta": ContextValidator.obtener_mensaje_restriccion(),
                "valida": False,
            }

        # ── 3. RAG + Gemini ──
        try:
            contexto = RAGService.buscar(pregunta)
            respuesta = GeminiService.generar_respuesta(contexto, pregunta)
            return {"respuesta": respuesta, "valida": True, "contexto": contexto}
        except ValueError as e:
            return {"respuesta": "Error de configuración: " + str(e), "valida": False}
        except RuntimeError as e:
            msg = str(e)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                return {
                    "respuesta": "El servicio de IA está temporalmente no disponible por límite de cuota. Intenta más tarde.",
                    "valida": False,
                }
            if "NOT_FOUND" in msg or "404" in msg:
                return {
                    "respuesta": "El modelo de IA configurado no está disponible. Revisa la configuración.",
                    "valida": False,
                }
            return {"respuesta": "Error del sistema: " + str(e), "valida": False}
        except Exception:
            return {"respuesta": "Ocurrió un error inesperado. Intenta de nuevo.", "valida": False}

