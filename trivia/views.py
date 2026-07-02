import json
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import IntegrityError

from .models import Partida, Pregunta, Respuesta
from .services import TriviaServices

# Vistas de autenticación y dashboard

def login_registro_view(request):
    """Muestra la página de inicio (Login y Registro combinados) o redirige si ya está autenticado."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_login = None
    error_registro = None

    if request.method == 'POST':
        action = request.POST.get('action')

        # Lógica de Login
        if action == 'login':
            identificacion = request.POST.get('identificacion')
            password = request.POST.get('password')

            user = authenticate(request, username=identificacion, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                error_login = "Número de identificación o contraseña incorrectos."

        # Lógica de Registro
        elif action == 'registro':
            nombre = request.POST.get('nombre')
            identificacion = request.POST.get('identificacion')
            password = request.POST.get('password')

            if not nombre or not identificacion or not password:
                error_registro = "Todos los campos son obligatorios."
            else:
                try:
                    # Crear usuario. Django hashea automáticamente la contraseña con create_user
                    user = User.objects.create_user(
                        username=identificacion,
                        password=password,
                        first_name=nombre
                    )
                    # Iniciar sesión automáticamente después de registrarse
                    login(request, user)
                    return redirect('dashboard')
                except IntegrityError:
                    error_registro = "El número de identificación ya se encuentra registrado."

    return render(request, 'trivia/login.html', {
        'error_login': error_login,
        'error_registro': error_registro
    })


@login_required(login_url='login_registro')
def dashboard_view(request):
    """Muestra el historial de partidas del jugador."""
    partidas = Partida.objects.filter(jugador=request.user).order_index = 0
    # Ordenar por fecha de creación descendente para mostrar la más reciente primero
    partidas = Partida.objects.filter(jugador=request.user).order_by('-fecha_creacion')
    return render(request, 'trivia/dashboard.html', {'partidas': partidas})


def logout_view(request):
    """Cierra la sesión del jugador."""
    logout(request)
    return redirect('login_registro')


@login_required(login_url='login_registro')
def juego_view(request):
    """Renderiza el tablero principal del juego (SPA)."""
    return render(request, 'trivia/juego.html')


# endpoints de la API JSON 

@login_required(login_url='login_registro')
@require_POST
def api_iniciar_juego(request):
    """Inicia una partida y retorna el estado inicial."""
    partida = TriviaServices.iniciar_partida(request.user)
    return JsonResponse({
        'status': 'success',
        'partida_id': partida.id,
        'ronda_actual': partida.ronda_actual,
        'puntaje': partida.puntaje,
        'estado': partida.estado
    })


@login_required(login_url='login_registro')
def api_obtener_pregunta(request):
    """Obtiene la pregunta del nivel actual para la partida activa del usuario."""
    partida = Partida.objects.filter(jugador=request.user, estado='EN_PROGRESO').first()
    if not partida:
        return JsonResponse({'status': 'error', 'message': 'No hay ninguna partida activa.'}, status=400)

    pregunta = TriviaServices.obtener_pregunta_aleatoria(partida)
    if not pregunta:
        return JsonResponse({
            'status': 'error',
            'message': 'No se encontraron preguntas configuradas para este nivel.'
        }, status=400)

    # Preparar las opciones de respuesta desordenadas aleatoriamente
    respuestas_query = list(pregunta.respuestas.all())
    random.shuffle(respuestas_query)
    respuestas_data = [{
        'id': r.id,
        'texto': r.texto
    } for r in respuestas_query]

    return JsonResponse({
        'status': 'success',
        'ronda_actual': partida.ronda_actual,
        'categoria': pregunta.categoria.nombre,
        'premio_ronda': pregunta.categoria.premio,
        'puntaje_actual': partida.puntaje,
        'pregunta_texto': pregunta.texto,
        'respuestas': respuestas_data
    })


@login_required(login_url='login_registro')
@require_POST
def api_verificar_respuesta(request):
    """Valida la respuesta seleccionada por el jugador y el tiempo transcurrido."""
    partida = Partida.objects.filter(jugador=request.user, estado='EN_PROGRESO').first()
    if not partida:
        return JsonResponse({'status': 'error', 'message': 'No hay ninguna partida activa.'}, status=400)

    try:
        data = json.loads(request.body)
        respuesta_id = data.get('respuesta_id')
        tiempo_transcurrido = int(data.get('tiempo_transcurrido', 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'}, status=400)

    es_correcta, mensaje = TriviaServices.verificar_respuesta(partida, respuesta_id, tiempo_transcurrido)

    return JsonResponse({
        'status': 'success',
        'es_correcta': es_correcta,
        'mensaje': mensaje,
        'ronda_actual': partida.ronda_actual,
        'puntaje': partida.puntaje,
        'estado': partida.estado
    })


@login_required(login_url='login_registro')
@require_POST
def api_retirarse(request):
    """Retira voluntariamente al jugador y guarda su puntaje."""
    partida = Partida.objects.filter(jugador=request.user, estado='EN_PROGRESO').first()
    if not partida:
        return JsonResponse({'status': 'error', 'message': 'No hay ninguna partida activa.'}, status=400)

    success, mensaje = TriviaServices.retirar_jugador(partida)
    return JsonResponse({
        'status': 'success' if success else 'error',
        'mensaje': mensaje,
        'puntaje': partida.puntaje,
        'estado': partida.estado
    })
