from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Categoria, Pregunta, Respuesta, Partida

# Validar que se guarde exactamente una respuesta correcta por pregunta
class RespuestaInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        correctas = 0
        total = 0
        
        for form in self.forms:
            # Si el formulario está marcado para eliminarse, lo ignoramos
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                total += 1
                if form.cleaned_data.get('es_correcta', False):
                    correctas += 1
                    
        if total > 0: # Solo validamos si hay respuestas cargadas
            if correctas == 0:
                raise ValidationError("Debes marcar exactamente una opción como correcta.")
            if correctas > 1:
                raise ValidationError("No puedes marcar más de una respuesta como correcta.")

# Editar respuestas en la misma pantalla de la pregunta 
class RespuestaInline(admin.TabularInline):
    model = Respuesta
    formset = RespuestaInlineFormSet
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