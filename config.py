"""Configuración compartida."""

import logging
import os
import time
from functools import wraps

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()  # lee ANTHROPIC_API_KEY (y MODEL, opcional) del archivo .env

VARIABLES_REQUERIDAS = ["ANTHROPIC_API_KEY"]


def validar_entorno() -> None:
    """Falla al inicio, con un mensaje claro, si falta alguna variable de entorno."""
    faltantes = [v for v in VARIABLES_REQUERIDAS if not os.getenv(v)]
    if faltantes:
        raise RuntimeError(
            f"Faltan variables de entorno: {', '.join(faltantes)}. "
            "Copiá .env.example a .env y completalas."
        )


validar_entorno()

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")

# Máximo de decisiones del supervisor. Evita el "supervisor infinito".
MAX_PASOS = 6

# Logger propio: solo muestra nuestros mensajes (no los de cada request HTTP de las librerías).
logger = logging.getLogger("orquestador")
logger.setLevel(logging.INFO)
if not logger.handlers:  # evita handlers duplicados si el módulo se recarga (ej. en el notebook)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)


def get_llm() -> ChatAnthropic:
    # Todos los agentes usan este mismo LLM, así la configuración es igual en todos lados.
    # No pasamos `temperature` porque claude-sonnet-5-5 no acepta valores distintos al
    # default (la API devuelve error). Se usa el default del modelo en todos los agentes.
    return ChatAnthropic(model=MODEL)


def medir_tiempo(nombre: str):
    """Decorador para los nodos del grafo: registra en el log cuánto tardó cada uno."""

    def decorador(funcion):
        @wraps(funcion)
        def envoltura(state):
            inicio = time.perf_counter()
            resultado = funcion(state)
            duracion = time.perf_counter() - inicio
            destino = f" -> {resultado['next_agent']}" if "next_agent" in resultado else ""
            logger.info("nodo %s%s (%.2f s)", nombre, destino, duracion)
            return resultado

        return envoltura

    return decorador
