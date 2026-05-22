from django.db import models
from django.contrib.auth.models import User


class Estudiante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="estudiante")
    matricula = models.CharField(max_length=20, unique=True)
    carrera = models.CharField(max_length=100, blank=True, default="")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.matricula}"


class Conversacion(models.Model):
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversaciones")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"Conversación {self.id} - {self.estudiante.username}"


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
