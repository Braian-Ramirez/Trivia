from django.urls import path
from . import views

urlpatterns = [
    # Vistas HTMLestándar
    path('', views.login_registro_view, name='login_registro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('juego/', views.juego_view, name='juego'),

    # Endpoints API JSON
    path('api/iniciar/', views.api_iniciar_juego, name='api_iniciar_juego'),
    path('api/pregunta/', views.api_obtener_pregunta, name='api_obtener_pregunta'),
    path('api/responder/', views.api_verificar_respuesta, name='api_verificar_respuesta'),
    path('api/retirarse/', views.api_retirarse, name='api_retirarse'),
]