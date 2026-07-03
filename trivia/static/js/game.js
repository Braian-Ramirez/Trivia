// === REFERENCIAS A ELEMENTOS DEL DOM ===
const screenStart = document.getElementById('screen-start');
const screenGame = document.getElementById('screen-game');
const screenResult = document.getElementById('screen-result');

const btnIniciar = document.getElementById('btn-iniciar');
const btnRetirarse = document.getElementById('btn-retirarse');
const btnJugarDeNuevo = document.getElementById('btn-jugar-de-nuevo');

const infoRonda = document.getElementById('info-ronda');
const infoPuntaje = document.getElementById('info-puntaje');
const infoCategoria = document.getElementById('info-categoria');
const infoPremioRonda = document.getElementById('info-premio-ronda');
const preguntaTexto = document.getElementById('pregunta-texto');
const respuestasContainer = document.getElementById('respuestas-container');

const timerDisplay = document.getElementById('timer-display');
const timerArc = document.getElementById('timer-arc');
const resultIcon = document.getElementById('result-icon');
const resultTitle = document.getElementById('result-title');
const resultMessage = document.getElementById('result-message');
const resultPuntaje = document.getElementById('result-puntaje');

// === ESTADO DEL JUEGO ===
let timerInterval = null;
let tiempoRestante = 60;
const TOTAL_TIEMPO = 60;
const CIRCUNFERENCIA = 2 * Math.PI * 54; // r=54

// Configurar el SVG del temporizador
timerArc.style.strokeDasharray = CIRCUNFERENCIA;
timerArc.style.strokeDashoffset = 0;

// === FUNCIONES DE PANTALLA ===
function showScreen(screen) {
    [screenStart, screenGame, screenResult].forEach(s => s.classList.add('hidden'));
    screen.classList.remove('hidden');
}

// === TEMPORIZADOR ===
function iniciarTemporizador() {
    detenerTemporizador();
    tiempoRestante = TOTAL_TIEMPO;
    actualizarDisplayTimer();

    timerInterval = setInterval(() => {
        tiempoRestante--;
        actualizarDisplayTimer();
        if (tiempoRestante <= 0) {
            detenerTemporizador();
            // Tiempo agotado: enviar tiempo > 60 para que el servidor lo detecte
            procesarRespuesta(null, 61);
        }
    }, 1000);
}

function detenerTemporizador() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function actualizarDisplayTimer() {
    timerDisplay.textContent = tiempoRestante;
    const progreso = (tiempoRestante / TOTAL_TIEMPO);
    const offset = CIRCUNFERENCIA * (1 - progreso);
    timerArc.style.strokeDashoffset = offset;

    // Cambiar color según el tiempo restante
    if (tiempoRestante <= 10) {
        timerArc.style.stroke = '#ef4444'; // rojo urgente
    } else if (tiempoRestante <= 20) {
        timerArc.style.stroke = '#f59e0b'; // amarillo advertencia
    } else {
        timerArc.style.stroke = '#22d3ee'; // azul cian normal
    }
}

// === LÓGICA DEL JUEGO ===
async function iniciarJuego() {
    const res = await fetch('/api/iniciar/', { method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN } });
    const data = await res.json();
    if (data.status === 'success') {
        showScreen(screenGame);
        cargarPregunta();
    }
}

async function cargarPregunta() {
    const res = await fetch('/api/pregunta/');
    const data = await res.json();

    if (data.status !== 'success') {
        mostrarResultado({ estado: 'PERDIDA', mensaje: data.message, puntaje: 0 });
        return;
    }

    // Actualizar la barra de estado
    infoRonda.textContent = `${data.ronda_actual} / 5`;
    infoPuntaje.textContent = `${data.puntaje_actual} pts`;
    infoCategoria.textContent = data.categoria;
    infoPremioRonda.textContent = `+${data.premio_ronda} pts`;
    preguntaTexto.textContent = data.pregunta_texto;

    // Generar los botones de respuesta
    respuestasContainer.innerHTML = '';
    data.respuestas.forEach(respuesta => {
        const btn = document.createElement('button');
        btn.classList.add('answer-btn');
        btn.textContent = respuesta.texto;
        btn.dataset.id = respuesta.id;
        btn.addEventListener('click', () => {
            const tiempoUsado = TOTAL_TIEMPO - tiempoRestante;
            procesarRespuesta(respuesta.id, tiempoUsado);
        });
        respuestasContainer.appendChild(btn);
    });

    iniciarTemporizador();
}

async function procesarRespuesta(respuestaId, tiempoTranscurrido) {
    detenerTemporizador();
    // Deshabilitar todos los botones para evitar doble clic
    document.querySelectorAll('.answer-btn').forEach(btn => btn.disabled = true);

    const res = await fetch('/api/responder/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify({ respuesta_id: respuestaId, tiempo_transcurrido: tiempoTranscurrido })
    });
    const data = await res.json();

    if (data.estado === 'EN_PROGRESO') {
        // Respuesta correcta, mostrar feedback y luego cargar la siguiente pregunta
        infoPuntaje.textContent = `${data.puntaje} pts`;
        preguntaTexto.textContent = `✅ ${data.mensaje}`;
        setTimeout(cargarPregunta, 1800);
    } else {
        // Partida terminada (GANADA o PERDIDA por tiempo/error)
        mostrarResultado(data);
    }
}

async function retirarJugador() {
    detenerTemporizador();
    const res = await fetch('/api/retirarse/', { method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN } });
    const data = await res.json();
    mostrarResultado(data);
}

function mostrarResultado(data) {
    showScreen(screenResult);

    if (data.estado === 'GANADA') {
        resultIcon.textContent = '🏆';
        resultTitle.textContent = '¡Ganaste el Juego!';
        resultTitle.className = 'result-title won';
    } else if (data.estado === 'RETIRADO') {
        resultIcon.textContent = '💰';
        resultTitle.textContent = '¡Te retiraste con tu premio!';
        resultTitle.className = 'result-title retired';
    } else {
        resultIcon.textContent = '💀';
        resultTitle.textContent = '¡Perdiste!';
        resultTitle.className = 'result-title lost';
    }
    resultMessage.textContent = data.mensaje;
    resultPuntaje.textContent = `${data.puntaje} pts`;
}

// === EVENTOS ===
btnIniciar.addEventListener('click', iniciarJuego);
btnRetirarse.addEventListener('click', retirarJugador);
btnJugarDeNuevo.addEventListener('click', iniciarJuego);
