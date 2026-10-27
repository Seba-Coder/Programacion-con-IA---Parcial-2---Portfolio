"""
Servidor MCP para juego de Batalla Naval en Python usando FastMCP.

Expone recursos y herramientas (tools) MCP para interactuar con la lógica del juego.
Convención de coordenadas: (x, y) = (columna, fila) de 0 a 5.
"""

from typing import Dict
from mcp.server.fastmcp import FastMCP
import juego

mcp = FastMCP("Batalla Naval MCP")


# --- MCP Resource ---
@mcp.resource("battleship://reglas")
def obtener_reglas() -> str:
    """
    Devuelve las reglas oficiales de la partida de Batalla Naval MCP.

    Retorna:
        str: Texto con el reglamento completo de la partida y formato de coordenadas.
    """
    return (
        "=== REGLAS DE BATALLA NAVAL MCP ===\n"
        "- Tablero: Matriz de 6x6 (coordenadas x=0..5, y=0..5).\n"
        "- Barcos por jugador: 3 barcos (uno de 3 casillas, uno de 2 casillas y uno de 1 casilla).\n"
        "- Ubicación: Colocados horizontal o verticalmente sin superponerse ni tocarse (incluso en diagonales).\n"
        "- Turnos: El jugador humano dispara indicando coordenadas (x, y) a la IA con 'disparar_a_ia'.\n"
        "  Luego, la IA responde disparando automáticamente al tablero del jugador con 'disparar_a_jugador'.\n"
        "- Resultados de disparo: 'agua', 'tocado' o 'hundido'.\n"
        "- Condición de victoria: Gana el primero en hundir todos los barcos del rival."
    )


# --- MCP Tools ---
@mcp.tool()
def iniciar_partida() -> str:
    """
    Inicia una nueva partida reseteando el estado y generando ambos tableros.

    Retorna:
        str: Mensaje de confirmación devuelto por la lógica del juego.
    """
    return juego.iniciar_partida()


@mcp.tool()
def disparar_a_ia(x: int, y: int) -> str:
    """
    Ejecuta un disparo del jugador contra el tablero de la IA en la coordenada indicada.

    Aplica la convención de coordenadas (x, y) = (columna, fila).

    Parámetros:
        x: Columna objetivo (0 a 5).
        y: Fila objetivo (0 a 5).

    Retorna:
        str: Mensaje descriptivo con el resultado ('agua', 'tocado', 'hundido')
             o mensaje de error si las coordenadas son inválidas, repetidas o la partida terminó.
    """
    return juego.disparar_a_ia(x, y)


@mcp.tool()
def disparar_a_jugador() -> str:
    """
    Decide automáticamente la coordenada con lógica hunt-and-target y ejecuta el disparo de la IA.

    Si hay casillas en la cola de persecución, dispara allí; si no, elige al azar en modo caza.
    En caso de 'tocado', agrega las adyacentes no probadas; si hunde el barco, vacía la cola.

    Retorna:
        str: Mensaje descriptivo con el resultado ('AGUA', 'TOCADO', 'HUNDIDO')
             o mensaje de error si la partida terminó o no hay casillas disponibles.
    """
    return juego.disparar_a_jugador()


@mcp.tool()
def obtener_estado_partida() -> Dict:
    """
    Devuelve la representación de ambos tableros y el estado interno de la IA.

    Aplica la convención de coordenadas (x, y) = (columna, fila).
    El tablero del jugador se ve completo con barcos e impactos; del tablero de la IA
    solo se muestran las casillas disparadas y descubiertas.

    Retorna:
        Dict: Diccionario con las claves 'tablero_jugador', 'tablero_ia_descubierto',
              'modo_ia', 'cola_persecucion_ia' y 'leyenda'.
    """
    return juego.obtener_estado_partida()


@mcp.tool()
def verificar_fin_juego() -> str:
    """
    Verifica si algún jugador ya hundió todos los barcos del otro.

    Retorna:
        str: Mensaje descriptivo indicando victoria del jugador, victoria de la IA,
             empate o si la partida continúa.
    """
    return juego.verificar_fin_juego()


if __name__ == "__main__":
    # Inicia el servidor FastMCP usando stdio por defecto
    mcp.run()
