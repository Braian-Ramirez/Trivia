from django.contrib import admin
from .models import Categoria, Pregunta, Respuesta, Partida

# Editar respuestas en la mismapantalla de la pregunta 
class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 4 # Espacios para las respuestas
    max_num = 4 # número de respuestas

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    inlines =  [RespuestaInline]  
    list_display = ('categoria', 'texto')
    list_filter = ('categoria',)
    search_fields = ('texto',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'premio')
    ordering = ('nivel',)

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'jugador', 'ronda_actual', 'puntaje', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)          