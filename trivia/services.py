from os import stat
import random
from django.shortcuts import get_list_or_404
from .models import Partida, Categoria, Pregunta, Respuesta

class TriviaServices:

    @staticmethod
    def iniciar_partida(jugador):
        """Crear e iniciar nueva partida"""
        # Si el jugador tiene una partida en progreso, la damos por perdida para evitar conflictos
        Partida.objects.filter(jugador=jugador, estado='EN_PROGRESO').update(estado='PERDIDA', puntaje=0)

        # Crear la nueva partida
        partida = Partida.objects.create(jugador=jugador, ronda_actual = 1, puntaje = 0, estado = 'EN_PROGRESO')
        return partida

    @staticmethod
    def obtener_pregunta_aleatoria(partida):
        """Obtiene una pregunta aleatoria según la ronda actual"""
        if partida.estado != 'EN_PROGRESO':
            return None

        #Buscar la categoría correspondiente a la ronda actual
        try:
            categoria = Categoria.objects.get(nivel=partida.ronda_actual) 
        except Categoria.DoesNotExist:
            #Si no existe la categoría para esta ronda, la partida termina en derrota
            partida.estado = 'PERDIDA'
            partida.save()
            return None

        # Obtener todas las preguntas de esa categoría 
        preguntas = list(categoria.preguntas.all())
        if not preguntas:
            return None

        # seleccionar una pregunta al azar
        return random.choice(preguntas)

    @staticmethod
    def verificar_respuesta(partida, respuesta_id, tiempo_transcurrido):
        """
        Verifica la respuesta enviada por el jugador
        -tiempo_trancurrido: tiempo en segundos que el jugador tradó en responder
        """   
        if partida.estado != 'EN_PROGRESO':
            return False, "La partida ha finalizado"

        # 1. Validar el temporizador en segundos
        if tiempo_transcurrido > 60:
            partida.estado = 'PERDIDA'
            partida.puntaje = 0
            partida.save()
            return False, "¡Tiempo agotado! Perdiste"  

        # 2. Validar que la respuesta sea correcta  
        try:
            respuesta = Respuesta.objects.get(id = respuesta_id)
        except Respuesta.DoesNotExist:
            return False, "La respuesta seleccionada no existe"

        # 3. Validar si la respuesta es correcta
        if respuesta.es_correcta:
            # Obtener puntaje de la categoría actual
            categoria = Categoria.objects.get(nivel=partida.ronda_actual)
            partida.puntaje += categoria.premio
            # Si es el último nivel o ronda (5), el jugador gana
            if partida.ronda_actual == 5:
                partida.estado = 'GANADA'
                partida.save()
                return True, "¡Felicidades! Has respondido correctamente la última ronda y ganaste el juego"

            else:
                # Avanzar a la siguiente ronda
                partida.ronda_actual += 1
                partida.save()
                return True, "¡Respuesta correcta! Pasas a la siguiente ronda"

        else:
            # Si la respuesta es incorrecta, pierde le puntaje acumulado y el juego
            partida.estado = 'PERDIDA'
            partida.puntaje = 0
            partida.save()
            return False, "¡Respuesta incorrecta! Perdiste"

    @staticmethod
    def retirar_jugador(partida):
        """El jugador se puede retirar voluntariamente conservando el puntaje acumulado"""
        if partida.estado != 'EN_PROGRESO':
            return False, "La partida ya ha finalizado"
            
        partida.estado = 'RETIRADO'
        partida.save()
        return True, f"Te has retirado de la partida. Puntaje acumulado: {partida.puntaje}"



                


        


