"""Configuración de pytest.

Ponemos una API key falsa para poder importar los módulos sin un .env real.
Ningún test llama a la API: solo se prueban herramientas, ruteo y condiciones de parada.
"""

import os

os.environ.setdefault("ANTHROPIC_API_KEY", "clave-falsa-para-tests")
