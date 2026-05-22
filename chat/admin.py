from django.contrib import admin
from .models import Estudiante, Conversacion, Pregunta, Respuesta


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ["matricula", "carrera", "fecha_registro"]
    search_fields = ["matricula", "user__username", "user__email"]


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ["id", "estudiante", "fecha_inicio", "activa"]
    list_filter = ["activa", "fecha_inicio"]
    search_fields = ["estudiante__username"]


class RespuestaInline(admin.StackedInline):
    model = Respuesta
    readonly_fields = ["fecha", "contexto_rag"]


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ["contenido", "conversacion", "fecha"]
    inlines = [RespuestaInline]
    readonly_fields = ["fecha"]


@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ["contenido", "pregunta", "fecha"]
    readonly_fields = ["fecha", "contexto_rag"]
