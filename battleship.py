"""
Servidor MCP para juego de Batalla Naval en Python usando FastMCP.
"""

from typing import Dict
from mcp.server.fastmcp import FastMCP
import juego

mcp = FastMCP("Batalla Naval MCP")


# --- MCP Resource ---
@mcp.resource("battleship://reglas")
def obtener_reglas() -> str:
    """Devuelve las reglas oficiales de la partida de Batalla Naval MCP."""
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
    """Genera ambos tableros al azar respetando las reglas de ubicación y resetea todo el estado."""
    return juego.iniciar_partida()


@mcp.tool()
def disparar_a_ia(x: int, y: int) -> str:
    """
    Recibe las coordenadas (x, y) donde el jugador desea disparar contra la IA.
    Valida las coordenadas, revisa si impacta y devuelve 'agua', 'tocado' o 'hundido'.
    """
    return juego.disparar_a_ia(x, y)


@mcp.tool()
def disparar_a_jugador() -> str:
    """
    Sin parámetros. Decide la coordenada automáticamente con lógica hunt-and-target.
    Si hay celdas pendientes en la cola de persecución, dispara allí. Si no, elige al azar.
    Agrega celdas adyacentes no probadas en caso de 'tocado'. Si lo hunde, vacía la cola.
    """
    return juego.disparar_a_jugador()


@mcp.tool()
def obtener_estado_partida() -> Dict:
    """
    Devuelve la representación en caracteres/diccionario de ambos tableros.
    El tablero del jugador se ve completo. De la IA solo se muestran los disparos e impactos descubiertos.
    """
    return juego.obtener_estado_partida()


@mcp.tool()
def verificar_fin_juego() -> str:
    """Verifica si algún jugador ya hundió todos los barcos del otro."""
    return juego.verificar_fin_juego()


if __name__ == "__main__":
    # Inicia el servidor FastMCP usando stdio por defecto
    mcp.run()
