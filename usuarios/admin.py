from django.contrib import admin
from .models import Estudiante


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ["user", "carrera", "fecha_registro"]
    search_fields = ["user__username", "user__email"]
