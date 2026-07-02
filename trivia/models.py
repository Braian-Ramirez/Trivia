from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):

    nombre = models.CharField(max_length= 100)
    nivel = models.IntegerField(unique=True, help_text= "Nivel de dificultad de la categoria (1-5)" )
    premio = models.IntegerField(default=0, help_text= "Premio en puntos por acertar una pregunta de esta categoria")

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel} - Premio: {self.premio})"

class Pregunta(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="preguntas")
    texto = models.TextField()

    def __str__(self):
        return self.texto

class Respuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name="respuestas")
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.texto} ({'Correcta' if self.es_correcta else 'Incorrecta'})"

class Partida(models.Model):
    ESTADOS = [
        ('EN_PROGRESO', 'En Progreso'),
        ('GANADA', 'Ganada (Ronda 5 superada)'),
        ('RETIRADO', 'Retiro voluntario del jugador'),
        ('PERDIDA', 'Perdida (Respuesta incorrecta)'),
    ]    
    
    jugador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="partidas")
    ronda_actual = models.IntegerField(default=1, help_text="Ronda/Nivel en el que está respondiendo")
    puntaje = models.IntegerField(default=0, help_text="Puntaje toatal acumulado hasta ahora")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='EN_PROGRESO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Partida {self.id} - {self.jugador.first_name} (Estado: {self.estado}, Acumulado: {self.puntaje})"
    
