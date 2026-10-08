"""Supervisor (router + validación) y Sintetizador (respuesta final)."""

from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from config import MAX_PASOS, get_llm
from state import OrquestadorState, formatear_aportes


class Decision(BaseModel):
    """Respuesta estructurada del supervisor."""

    siguiente: Literal["investigador", "analista", "FINISH"] = Field(
        description="Quién interviene ahora, o FINISH si la tarea está completa."
    )
    instruccion: str = Field(
        description="Tarea concreta para el especialista elegido. Vacío si es FINISH."
    )
    motivo: str = Field(description="Por qué tomaste esta decisión (una oración).")


SUPERVISOR_PROMPT = """Sos el Supervisor de un equipo de agentes de Supermercados del Valle.
Dada la conversación actual, decidí quién debe intervenir ahora o si es momento de finalizar.

Especialistas disponibles:
- investigador: BUSCA datos en fuentes externas (reseñas de clientes, precios de la
  competencia, noticias del mercado). No hace cálculos.
- analista: PROCESA datos ya obtenidos (análisis de sentimiento, comparación de precios).
  No busca datos nuevos, así que solo puede trabajar después del investigador.

Rúbrica de validación (para elegir FINISH TODAS deben cumplirse):
1. El investigador trajo datos concretos para cada parte del pedido del usuario.
2. Si el pedido requiere análisis o cálculos, el analista los hizo con esos datos y
   muestra números.
3. Los aportes no se contradicen entre sí. Si hay una contradicción o un dato faltante,
   mandá al especialista que corresponda con una instrucción que diga qué corregir.

Reglas:
- Dale al especialista una instrucción concreta y autocontenida (él no ve el historial).
- No repitas una instrucción que ya se cumplió.
- Si un dato no existe en las fuentes, aceptalo como "no disponible" y no insistas."""


SINTETIZADOR_PROMPT = """Sos el redactor final del equipo de Supermercados del Valle.
Con el pedido del usuario y los aportes de los especialistas, escribí una respuesta final
clara y breve en español. Usá solo la información de los aportes, sin inventar datos.
Terminá con una recomendación concreta."""


llm = get_llm()
llm_supervisor = llm.with_structured_output(Decision, method="json_schema")


def nodo_supervisor(state: OrquestadorState) -> dict:
    pasos = state.get("pasos", 0)

    # Condición de parada dura: si se llegó al límite, se termina sí o sí.
    if pasos >= MAX_PASOS:
        return {
            "next_agent": "FINISH",
            "task_completed": True,
            "messages": [AIMessage(f"Límite de {MAX_PASOS} pasos alcanzado: finalizo.", name="supervisor")],
        }

    pedido = state["messages"][0].text
    contexto = (
        f"Pedido del usuario:\n{pedido}\n\n"
        f"Aportes de los especialistas hasta ahora:\n{formatear_aportes(state.get('aportes', []))}\n\n"
        f"Paso {pasos + 1} de {MAX_PASOS}."
    )
    decision: Decision = llm_supervisor.invoke([SystemMessage(SUPERVISOR_PROMPT), HumanMessage(contexto)])

    return {
        "next_agent": decision.siguiente,
        "instruccion": decision.instruccion,
        "pasos": pasos + 1,
        "task_completed": decision.siguiente == "FINISH",
        "messages": [AIMessage(f"-> {decision.siguiente}: {decision.motivo}", name="supervisor")],
    }


def elegir_siguiente(state: OrquestadorState) -> Literal["investigador", "analista", "sintetizador"]:
    """Arista condicional: traduce la decisión del supervisor al nombre de un nodo."""
    if state["next_agent"] == "FINISH":
        return "sintetizador"
    return state["next_agent"]


def nodo_sintetizador(state: OrquestadorState) -> dict:
    pedido = state["messages"][0].text
    contexto = f"Pedido del usuario:\n{pedido}\n\nAportes:\n{formatear_aportes(state['aportes'])}"
    respuesta = llm.invoke([SystemMessage(SINTETIZADOR_PROMPT), HumanMessage(contexto)])
    return {"messages": [AIMessage(respuesta.text, name="sintetizador")]}
