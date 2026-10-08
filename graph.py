"""Grafo principal: Supervisor + especialistas + sintetizador."""

from langgraph.graph import END, START, StateGraph

from agents.analyst_agent import nodo_analista
from agents.research_agent import nodo_investigador
from state import OrquestadorState
from supervisor import elegir_siguiente, nodo_sintetizador, nodo_supervisor


def construir_grafo():
    grafo = StateGraph(OrquestadorState)

    grafo.add_node("supervisor", nodo_supervisor)
    grafo.add_node("investigador", nodo_investigador)
    grafo.add_node("analista", nodo_analista)
    grafo.add_node("sintetizador", nodo_sintetizador)

    # Todo empieza en el supervisor
    grafo.add_edge(START, "supervisor")

    # El supervisor decide a quién mandar la tarea
    grafo.add_conditional_edges("supervisor", elegir_siguiente)

    # Los especialistas siempre le devuelven el control al supervisor
    grafo.add_edge("investigador", "supervisor")
    grafo.add_edge("analista", "supervisor")

    grafo.add_edge("sintetizador", END)
    return grafo.compile()


app = construir_grafo()
