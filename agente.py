"""
Módulo del Agente Capitán para Batalla Naval.
Carga la definición y prompt del agente desde prompts_agentes/capitan.agent.md
y se conecta con Ollama para narrar en personaje los disparos decididos por la lógica del juego.
"""

import json
import random
from typing import Dict, Any, Optional
import ollama

import juego

# --- Constantes de configuración ---
RUTA_AGENTE = "prompts_agentes/capitan.agent.md"
TEMPERATURA = 0.3
NUM_CTX = 4096


def cargar_agente(ruta: str = RUTA_AGENTE) -> dict:
    """
    Lee un archivo de agente en formato Markdown con frontmatter YAML,
    separa el frontmatter del cuerpo y devuelve la configuración estructurada del agente.

    Parámetros:
        ruta: Ruta al archivo Markdown del agente (por defecto RUTA_AGENTE).

    Retorna:
        dict con las claves:
            - 'name': Nombre del agente.
            - 'description': Descripción del agente.
            - 'model': Nombre del modelo LLM a utilizar.
            - 'system_prompt': Cuerpo Markdown que actúa como prompt de sistema.
    """
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    partes = contenido.split("---", 2)
    if len(partes) < 3:
        raise ValueError(f"El archivo {ruta} no contiene un frontmatter YAML válido delimitado por '---'.")

    frontmatter_str = partes[1].strip()
    system_prompt = partes[2].strip()

    datos = {}
    for linea in frontmatter_str.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            clave = clave.strip()
            valor = valor.strip().strip('"\'')
            datos[clave] = valor

    return {
        "name": datos.get("name", ""),
        "description": datos.get("description", ""),
        "model": datos.get("model", ""),
        "system_prompt": system_prompt
    }


def narrar_disparo(decision: dict, agente: dict) -> str:
    """
    Llama a ollama.chat con el system_prompt del agente y el JSON de la decisión
    como mensaje de usuario para narrar la orden de disparo en personaje.
    Verifica que la respuesta contenga las coordenadas exactas en formato '(x, y)';
    si no, reintenta hasta 2 veces. Si continúa fallando, retorna un mensaje de respaldo fijo.

    Parámetros:
        decision: Diccionario con campos 'x', 'y', 'modo' y 'motivo'.
        agente: Diccionario obtenido mediante cargar_agente.

    Retorna:
        str con la narración del Capitán con las coordenadas correctas.
    """
    x = decision["x"]
    y = decision["y"]
    coord_esperada = f"({x}, {y})"
    user_content = json.dumps(decision, ensure_ascii=False)

    max_reintentos = 2
    for intento in range(1 + max_reintentos):
        respuesta = ollama.chat(
            model=agente["model"],
            messages=[
                {"role": "system", "content": agente["system_prompt"]},
                {"role": "user", "content": user_content}
            ],
            options={"temperature": TEMPERATURA, "num_ctx": NUM_CTX}
        )
        contenido = respuesta["message"]["content"].strip()
        if coord_esperada in contenido:
            return contenido

    # Mensaje de respaldo fijo si todos los intentos fallan la verificación
    return f"¡Fuego en ({x}, {y})! Coordenadas confirmadas por el Capitán."


def responder_mensaje(texto: str, agente: dict) -> str:
    """
    Envía texto libre al agente a través de ollama.chat con el system_prompt
    para probar el comportamiento y los límites del rol en personaje.

    Parámetros:
        texto: Cadena de texto libre ingresada por el usuario.
        agente: Diccionario obtenido mediante cargar_agente.

    Retorna:
        str con la respuesta del Capitán.
    """
    respuesta = ollama.chat(
        model=agente["model"],
        messages=[
            {"role": "system", "content": agente["system_prompt"]},
            {"role": "user", "content": texto}
        ],
        options={"temperature": TEMPERATURA, "num_ctx": NUM_CTX}
    )
    return respuesta["message"]["content"].strip()


def main():
    """Demostración del Agente Capitán narrando decisiones de disparo y respondiendo consultas."""
    print("=== CARGANDO AGENTE CAPITÁN ===")
    agente = cargar_agente(RUTA_AGENTE)
    print(f"Nombre: {agente['name']}")
    print(f"Modelo: {agente['model']}")
    print(f"Descripción: {agente['description']}")
    print()

    # Caso 1: Modo Caza (usando random.Random(42))
    print("--- 1. Caso Modo Caza (semilla 42) ---")
    rng = random.Random(42)
    shots_caza = {(0, 0), (1, 1), (2, 2)}
    decision_caza = juego.decidir_disparo(
        ai_shots=shots_caza,
        ai_target_queue=[],
        board_size=6,
        rng=rng
    )
    print("Decisión (JSON):")
    print(json.dumps(decision_caza, indent=2, ensure_ascii=False))
    print("Narración del Capitán:")
    narracion_caza = narrar_disparo(decision_caza, agente)
    print(narracion_caza)
    print()

    # Caso 2: Modo Persecución (con cola de ejemplo)
    print("--- 2. Caso Modo Persecución ---")
    shots_persecucion = {(2, 4), (3, 4)}
    queue_persecucion = [(3, 4), (1, 4), (2, 5), (2, 3)]
    decision_persecucion = juego.decidir_disparo(
        ai_shots=shots_persecucion,
        ai_target_queue=queue_persecucion,
        board_size=6
    )
    print("Decisión (JSON):")
    print(json.dumps(decision_persecucion, indent=2, ensure_ascii=False))
    print("Narración del Capitán:")
    narracion_persecucion = narrar_disparo(decision_persecucion, agente)
    print(narracion_persecucion)
    print()

    # Caso 3: Prueba de rol con mensaje libre
    print("--- 3. Prueba de Rol (mensaje ajeno a la batalla) ---")
    pregunta = "¿Cuál es la receta de la paella de mariscos?"
    print(f"Pregunta: {pregunta}")
    respuesta_rol = responder_mensaje(pregunta, agente)
    print(f"Respuesta del Capitán:\n{respuesta_rol}")


if __name__ == "__main__":
    main()
