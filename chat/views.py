import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import ChatbotService
from .models import Conversacion, Pregunta, Respuesta


class ChatView(LoginRequiredMixin, View):
    """Vista principal del chat. Solo accesible con sesión iniciada."""

    login_url = "/usuarios/login/"

    def get(self, request):
        return render(request, "chat/chat.html")


class EnviarPreguntaView(LoginRequiredMixin, View):
    """Vista AJAX que procesa preguntas. Solo para usuarios autenticados."""

    login_url = "/usuarios/login/"
    chatbot_service = ChatbotService()

    def post(self, request):
        try:
            data = json.loads(request.body)
            pregunta_texto = data.get("pregunta", "").strip()

            if not pregunta_texto:
                return JsonResponse(
                    {"error": "La pregunta no puede estar vacía."}, status=400
                )

            resultado = self.chatbot_service.procesar_pregunta(pregunta_texto)

            self._guardar_en_bd(request, pregunta_texto, resultado)

            return JsonResponse(resultado)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def _guardar_en_bd(self, request, pregunta_texto: str, resultado: dict):
        conversacion, _ = Conversacion.objects.get_or_create(
            estudiante=request.user, activa=True
        )
        pregunta_obj = Pregunta.objects.create(
            conversacion=conversacion, contenido=pregunta_texto
        )
        Respuesta.objects.create(
            pregunta=pregunta_obj,
            contenido=resultado.get("respuesta", ""),
            contexto_rag=resultado.get("contexto", ""),
        )
