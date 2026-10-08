"""Demo por consola: muestra cómo el supervisor delega la tarea paso a paso.

Uso:
    python main.py
    python main.py "tu pregunta"
"""

import sys

from graph import app

PREGUNTA = (
    "¿Qué opinan los clientes de nuestra yerba y estamos caros o baratos frente a la "
    "competencia? Quiero el porcentaje de reseñas positivas y la diferencia de precio."
)


def main() -> None:
    pregunta = sys.argv[1] if len(sys.argv) > 1 else PREGUNTA
    print(f"USUARIO: {pregunta}\n")

    # stream_mode="updates" devuelve lo que escribió cada nodo apenas termina
    for paso in app.stream({"messages": [("user", pregunta)]}, stream_mode="updates"):
        for nodo, cambios in paso.items():
            print(f"===== {nodo.upper()} =====")
            print(cambios["messages"][-1].text, "\n")


if __name__ == "__main__":
    main()
