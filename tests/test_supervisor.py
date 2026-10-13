"""Tests del ruteo del supervisor, la condición de parada y la validación del entorno."""

import pytest

import config
import supervisor


def test_elegir_siguiente_mapea_a_nodos():
    assert supervisor.elegir_siguiente({"next_agent": "investigador"}) == "investigador"
    assert supervisor.elegir_siguiente({"next_agent": "analista"}) == "analista"
    assert supervisor.elegir_siguiente({"next_agent": "FINISH"}) == "sintetizador"


class LLMQueNoDebeLlamarse:
    def invoke(self, *args, **kwargs):
        raise AssertionError("Con el límite alcanzado, el supervisor no debería llamar al LLM")


def test_supervisor_corta_al_llegar_a_max_pasos(monkeypatch):
    monkeypatch.setattr(supervisor, "llm_supervisor", LLMQueNoDebeLlamarse())
    estado = {"messages": [], "aportes": [], "pasos": config.MAX_PASOS}

    resultado = supervisor.nodo_supervisor(estado)

    assert resultado["next_agent"] == "FINISH"
    assert resultado["task_completed"] is True
    assert supervisor.elegir_siguiente(resultado) == "sintetizador"


def test_validar_entorno_falla_si_falta_la_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        config.validar_entorno()
