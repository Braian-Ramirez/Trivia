from django.test import TestCase
from django.contrib.auth.models import User
from .models import Categoria, Pregunta, Respuesta, Partida
from .services import TriviaServices

class TriviaTestCase(TestCase):
    def setUp(self):
        # 1. Crear un usuario de prueba
        self.user = User.objects.create_user(
            username='12345678', 
            password='password123', 
            first_name='Jugador Prueba'
        )
        
        # 2. Crear categorías de prueba
        self.cat_nivel_1 = Categoria.objects.create(nombre='Básico', nivel=1, premio=100)
        self.cat_nivel_2 = Categoria.objects.create(nombre='Fácil', nivel=2, premio=250)
        
        # 3. Crear una pregunta para el nivel 1
        self.pregunta = Pregunta.objects.create(
            texto='¿Cuál es el lenguaje de programación de Django?', 
            categoria=self.cat_nivel_1
        )
        
        # 4. Crear respuestas para esa pregunta
        self.resp_correcta = Respuesta.objects.create(texto='Python', es_correcta=True, pregunta=self.pregunta)
        self.resp_incorrecta = Respuesta.objects.create(texto='JavaScript', es_correcta=False, pregunta=self.pregunta)

    def test_creacion_partida(self):
        """Verifica que una partida nueva se inicialice correctamente."""
        partida = TriviaServices.iniciar_partida(self.user)
        self.assertEqual(partida.jugador, self.user)
        self.assertEqual(partida.ronda_actual, 1)
        self.assertEqual(partida.puntaje, 0)
        self.assertEqual(partida.estado, 'EN_PROGRESO')

    def test_verificar_respuesta_correcta(self):
        """Verifica la lógica cuando el jugador acierta la pregunta."""
        partida = TriviaServices.iniciar_partida(self.user)
        
        es_correcta, mensaje = TriviaServices.verificar_respuesta(
            partida, 
            respuesta_id=self.resp_correcta.id, 
            tiempo_transcurrido=15
        )
        
        self.assertTrue(es_correcta)
        self.assertEqual(partida.ronda_actual, 2)  # Pasó a la ronda 2
        self.assertEqual(partida.puntaje, 100)     # Ganó los 100 pts de la categoría 1
        self.assertEqual(partida.estado, 'EN_PROGRESO')

    def test_verificar_respuesta_incorrecta(self):
        """Verifica la lógica cuando el jugador falla y pierde todo."""
        partida = TriviaServices.iniciar_partida(self.user)
        
        es_correcta, mensaje = TriviaServices.verificar_respuesta(
            partida, 
            respuesta_id=self.resp_incorrecta.id, 
            tiempo_transcurrido=15
        )
        
        self.assertFalse(es_correcta)
        self.assertEqual(partida.puntaje, 0)       # Pierde sus puntos
        self.assertEqual(partida.estado, 'PERDIDA') # Fin del juego
