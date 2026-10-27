import sys
from pathlib import Path
import random
import pytest

# Asegurar que la raíz del proyecto esté en sys.path para importar juego
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import juego


@pytest.fixture(autouse=True)
def inicializar_partida_con_semilla():
    """Fija la semilla aleatoria en 0 y reinicia la partida antes de cada test."""
    random.seed(0)
    juego.iniciar_partida()


def fijar_disposicion_barcos():
    """
    Helper que reemplaza los barcos de AMBOS jugadores por una disposición fija
    y limpia disparos, impactos, modo y cola de persecución.
    Barcos:
      - Barco de tamaño 3: {(0, 0), (1, 0), (2, 0)}
      - Barco de tamaño 2: {(4, 2), (4, 3)}
      - Barco de tamaño 1: {(0, 5)}
    """
    barcos = [
        {(0, 0), (1, 0), (2, 0)},
        {(4, 2), (4, 3)},
        {(0, 5)}
    ]
    coords = set().union(*barcos)

    # Actualizar barcos y coordenadas del jugador
    juego.game_state.player_ships = [set(b) for b in barcos]
    juego.game_state.player_ship_coords = set(coords)

    # Actualizar barcos y coordenadas de la IA
    juego.game_state.ai_ships = [set(b) for b in barcos]
    juego.game_state.ai_ship_coords = set(coords)

    # Limpiar disparos e impactos
    juego.game_state.player_shots.clear()
    juego.game_state.ai_shots.clear()
    juego.game_state.player_hits.clear()
    juego.game_state.ai_hits.clear()

    # Reiniciar autómata de la IA
    juego.game_state.ai_mode = "caza"
    juego.game_state.ai_target_queue.clear()

    return {
        "barcos": barcos,
        "coords": coords,
        "barco_3": {(0, 0), (1, 0), (2, 0)},
        "barco_2": {(4, 2), (4, 3)},
        "barco_1": {(0, 5)}
    }


@pytest.fixture
def colocar_barcos():
    """Fixture que expone y ejecuta fijar_disposicion_barcos."""
    return fijar_disposicion_barcos
