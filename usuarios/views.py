from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import Estudiante


class SignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("chat")
        return render(request, "usuarios/signup.html")

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        carrera  = request.POST.get("carrera", "").strip()

        if not all([username, password]):
            return render(request, "usuarios/signup.html", {
                "error": "Usuario y contraseña son obligatorios."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "usuarios/signup.html", {
                "error": "El usuario ya existe."
            })

        user = User.objects.create_user(username=username, password=password)
        Estudiante.objects.create(user=user, carrera=carrera)
        login(request, user)
        return redirect("chat")


class LoginView(View):
    def get(self, request):
        # Si ya está autenticado, redirigir al chat
        if request.user.is_authenticated:
            return redirect("chat")
        return render(request, "usuarios/login.html")

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not all([username, password]):
            return render(request, "usuarios/login.html", {
                "error": "Debes ingresar usuario y contraseña."
            })

        # authenticate verifica las credenciales contra la BD
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Crea la sesión
            # Redirige a ?next= si existe, si no al chat
            next_url = request.GET.get("next", "chat")
            return redirect(next_url)
        else:
            return render(request, "usuarios/login.html", {
                "error": "Usuario o contraseña incorrectos."
            })


class LogoutView(View):
    def post(self, request):
        logout(request)  # Destruye la sesión
        return redirect("login")

    # GET como fallback (por si acceden por link directo)
    def get(self, request):
        logout(request)
        return redirect("login")