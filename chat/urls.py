from django.urls import path
from . import views

urlpatterns = [
    path("", views.ChatView.as_view(), name="chat"),
    path("enviar/", views.EnviarPreguntaView.as_view(), name="enviar_pregunta"),
]
