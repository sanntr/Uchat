from django.db import models
from django.contrib.auth.models import User


class Conversacion(models.Model):
    estudiante = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name="conversaciones"
    )
    session_key = models.CharField(max_length=40, blank=True, default="")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        identificador = self.estudiante.username if self.estudiante else self.session_key[:20]
        return f"Conversación {self.id} - {identificador}"


class Pregunta(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name="preguntas")
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        ordering = ["fecha"]

    def __str__(self):
        return self.contenido[:75]


class Respuesta(models.Model):
    pregunta = models.OneToOneField(Pregunta, on_delete=models.CASCADE, related_name="respuesta")
    contenido = models.TextField()
    contexto_rag = models.TextField(blank=True, help_text="Contexto recuperado de FAISS para esta respuesta")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"

    def __str__(self):
        return self.contenido[:75]
