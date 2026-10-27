"""
Lógica pura del juego de Batalla Naval sin dependencias de MCP.
"""

import random
from typing import Dict, List, Tuple, Set, Optional

# --- Constantes y Configuración del Juego ---
BOARD_SIZE = 6
SHIP_SIZES = [3, 2, 1]  # 3 barcos: 3 casillas, 2 casillas, 1 casilla


# --- Estado Global del Juego ---
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        # Barcos: conjunto de tuplas (x, y) ocupadas por barcos
        # Mapeo de barco_id a conjunto de coordenadas para verificar cuando se hunde
        self.player_ships: List[Set[Tuple[int, int]]] = []
        self.ai_ships: List[Set[Tuple[int, int]]] = []

        # Coordenadas ocupadas totales
        self.player_ship_coords: Set[Tuple[int, int]] = set()
        self.ai_ship_coords: Set[Tuple[int, int]] = set()

        # Tiros realizados (x, y)
        self.player_shots: Set[Tuple[int, int]] = set()
        self.ai_shots: Set[Tuple[int, int]] = set()

        # Impactos
        self.player_hits: Set[Tuple[int, int]] = set()
        self.ai_hits: Set[Tuple[int, int]] = set()

        # IA State: 'caza' o 'persecucion'
        self.ai_mode: str = "caza"
        self.ai_target_queue: List[Tuple[int, int]] = []
        
        # Generar tableros
        self.player_ships, self.player_ship_coords = self._generate_board()
        self.ai_ships, self.ai_ship_coords = self._generate_board()

    def _generate_board(self) -> Tuple[List[Set[Tuple[int, int]]], Set[Tuple[int, int]]]:
        """Genera barcos aleatorios sin superposición ni adyacencia (horizontal/vertical/diagonal)."""
        all_ships: List[Set[Tuple[int, int]]] = []
        occupied: Set[Tuple[int, int]] = set()
        forbidden: Set[Tuple[int, int]] = set()

        for size in SHIP_SIZES:
            placed = False
            attempts = 0
            while not placed and attempts < 500:
                attempts += 1
                orientation = random.choice(["H", "V"])
                if orientation == "H":
                    start_x = random.randint(0, BOARD_SIZE - size)
                    start_y = random.randint(0, BOARD_SIZE - 1)
                    coords = {(start_x + i, start_y) for i in range(size)}
                else:
                    start_x = random.randint(0, BOARD_SIZE - 1)
                    start_y = random.randint(0, BOARD_SIZE - size)
                    coords = {(start_x, start_y + i) for i in range(size)}

                # Verificar si interseca con casillas ocupadas o prohibidas (adyacentes)
                if any(c in forbidden or c in occupied for c in coords):
                    continue

                # Colocado exitosamente
                all_ships.append(coords)
                occupied.update(coords)

                # Marcar zonas prohibidas (casillas ocupadas y sus 8 vecinos)
                for cx, cy in coords:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                                forbidden.add((nx, ny))

                placed = True

            if not placed:
                # Reiniciar si por azar quedó acorralado
                return self._generate_board()

        return all_ships, occupied


game_state = GameState()


def iniciar_partida() -> str:
    """Genera ambos tableros al azar respetando las reglas de ubicación y resetea todo el estado."""
    game_state.reset()
    return "Nueva partida iniciada. Ambos tableros fueron generados y el estado fue reseteado."


def disparar_a_ia(x: int, y: int) -> str:
    """
    Recibe las coordenadas (x, y) donde el jugador desea disparar contra la IA.
    Valida las coordenadas, revisa si impacta y devuelve 'agua', 'tocado' o 'hundido'.
    """
    if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
        return f"Error: Coordenadas ({x}, {y}) fuera de rango (0 a 5)."

    coord = (x, y)
    if coord in game_state.player_shots:
        return f"Ya habías disparado anteriormente en la coordenada ({x}, {y}). Elegí otra."

    game_state.player_shots.add(coord)

    # Recomprobar si impacta en algún barco de la IA
    if coord in game_state.ai_ship_coords:
        game_state.player_hits.add(coord)
        
        # Verificar si el barco específico fue completado (hundido)
        for ship in game_state.ai_ships:
            if coord in ship:
                if ship.issubset(game_state.player_hits):
                    return f"¡Impacto en ({x}, {y})! HUNDIDO. Hundiste un barco de la IA de tamaño {len(ship)}."
                else:
                    return f"¡Impacto en ({x}, {y})! TOCADO."

    return f"Disparo en ({x}, {y}): AGUA."


def decidir_disparo(ai_shots, ai_target_queue, board_size, rng=None) -> dict:
    """
    Decide el próximo disparo de la IA sin ejecutarlo y sin modificar sus argumentos.

    Parámetros:
        ai_shots: Colección o conjunto de coordenadas (x, y) ya disparadas por la IA.
        ai_target_queue: Lista de coordenadas (x, y) pendientes en la cola de persecución.
        board_size: Dimensión del tablero cuadrado (N x N).
        rng: Instancia opcional de random.Random para decisiones deterministas. Si es None, usa random.

    Retorna:
        dict con el siguiente formato:
        {
            "x": int,
            "y": int,
            "modo": "caza" | "persecucion",
            "motivo": str
        }

    Lanza:
        ValueError: Si no quedan casillas disponibles en el tablero para disparar.
    """
    # 1. Modo persecución: buscar la primera casilla de la cola no disparada
    for coord in ai_target_queue:
        if coord not in ai_shots:
            return {
                "x": coord[0],
                "y": coord[1],
                "modo": "persecucion",
                "motivo": "Objetivo pendiente en cola de persecución"
            }

    # 2. Modo caza: elegir al azar una casilla no disparada
    untried = [
        (x, y)
        for x in range(board_size)
        for y in range(board_size)
        if (x, y) not in ai_shots
    ]

    if not untried:
        raise ValueError("No quedan casillas disponibles para disparar.")

    chooser = rng if rng is not None else random
    chosen_x, chosen_y = chooser.choice(untried)

    return {
        "x": chosen_x,
        "y": chosen_y,
        "modo": "caza",
        "motivo": "Disparo aleatorio en modo caza"
    }


def ejecutar_disparo_ia(x: int, y: int) -> str:
    """
    Aplica un disparo de la IA en la casilla indicada (x, y) contra el tablero del jugador.

    Registra el disparo, actualiza impactos, modo y cola de persecución:
    - En caso de 'tocado', agrega a la cola las 4 casillas adyacentes válidas no disparadas y pasa a modo 'persecucion'.
    - En caso de 'hundido', vacía la cola y regresa a modo 'caza'.
    - Quita de la cola la casilla disparada y todas las casillas ya disparadas.

    Devuelve un mensaje con el resultado: agua, tocado o hundido.
    """
    target = (x, y)
    game_state.ai_shots.add(target)

    # Quitar de la cola la casilla disparada y las ya disparadas
    game_state.ai_target_queue = [
        coord for coord in game_state.ai_target_queue
        if coord != target and coord not in game_state.ai_shots
    ]

    # Evaluar disparo en el tablero del jugador
    if target in game_state.player_ship_coords:
        game_state.ai_hits.add(target)

        # Buscar qué barco del jugador fue impactado
        for ship in game_state.player_ships:
            if target in ship:
                if ship.issubset(game_state.ai_hits):
                    # Hundido -> vaciar cola de objetivos y volver a modo caza
                    game_state.ai_mode = "caza"
                    game_state.ai_target_queue.clear()
                    return f"La IA disparó en ({x}, {y}): HUNDIDO un barco tuyo de tamaño {len(ship)}."
                else:
                    # Tocado -> Entrar/mantener modo persecución y agregar 4 adyacentes
                    game_state.ai_mode = "persecucion"
                    adjacent = [
                        (x + 1, y), (x - 1, y),
                        (x, y + 1), (x, y - 1)
                    ]
                    for adj in adjacent:
                        ax, ay = adj
                        if 0 <= ax < BOARD_SIZE and 0 <= ay < BOARD_SIZE:
                            if adj not in game_state.ai_shots and adj not in game_state.ai_target_queue:
                                game_state.ai_target_queue.append(adj)
                    return f"La IA disparó en ({x}, {y}): TOCADO."

    # Si es agua, actualizar modo según si quedan objetivos pendientes en la cola
    if not game_state.ai_target_queue:
        game_state.ai_mode = "caza"
    else:
        game_state.ai_mode = "persecucion"

    return f"La IA disparó en ({x}, {y}): AGUA."


def disparar_a_jugador() -> str:
    """
    Sin parámetros. Decide automáticamente la coordenada con lógica hunt-and-target
    y ejecuta el disparo contra el tablero del jugador.
    Combina decidir_disparo y ejecutar_disparo_ia.
    """
    try:
        decision = decidir_disparo(
            ai_shots=game_state.ai_shots,
            ai_target_queue=game_state.ai_target_queue,
            board_size=BOARD_SIZE
        )
    except ValueError:
        return "La IA no tiene casillas disponibles para disparar."

    return ejecutar_disparo_ia(decision["x"], decision["y"])


def obtener_estado_partida() -> Dict:
    """
    Devuelve la representación en caracteres/diccionario de ambos tableros.
    El tablero del jugador se ve completo. De la IA solo se muestran los disparos e impactos descubiertos.
    """
    player_grid = []
    for y in range(BOARD_SIZE):
        row = []
        for x in range(BOARD_SIZE):
            coord = (x, y)
            if coord in game_state.player_hits:
                row.append("X")  # Tocado / Hundido
            elif coord in game_state.player_shots:
                row.append("O")  # Agua
            elif coord in game_state.player_ship_coords:
                row.append("B")  # Barco visible
            else:
                row.append("~")  # Agua oculta
        player_grid.append(" ".join(row))

    ai_grid = []
    for y in range(BOARD_SIZE):
        row = []
        for x in range(BOARD_SIZE):
            coord = (x, y)
            if coord in game_state.ai_hits:
                row.append("X")  # Tocado / Hundido
            elif coord in game_state.player_shots:
                row.append("O")  # Agua
            else:
                row.append("~")  # Oculto / Desconocido
        ai_grid.append(" ".join(row))

    return {
        "tablero_jugador": player_grid,
        "tablero_ia_descubierto": ai_grid,
        "modo_ia": game_state.ai_mode,
        "cola_persecucion_ia": [f"({x},{y})" for x, y in game_state.ai_target_queue],
        "leyenda": "~: Oculto/Agua, B: Barco tuyo, O: Disparo al agua, X: Disparo acertado"
    }


def verificar_fin_juego() -> str:
    """Verifica si algún jugador ya hundió todos los barcos del otro."""
    player_won = game_state.ai_ship_coords.issubset(game_state.player_hits)
    ai_won = game_state.player_ship_coords.issubset(game_state.ai_hits)

    if player_won and ai_won:
        return "¡Empate! Ambos hundieron el último barco en el mismo turno."
    elif player_won:
        return "¡Ganaste la partida! Hundiste todos los barcos de la IA."
    elif ai_won:
        return "¡La IA ganó la partida! Hundió todos tus barcos."
    else:
        return "La partida continúa. Aún hay barcos a flote en ambos lados."


#función que cuenta el total de disparos hechos por el jugador e ia
def contar_disparos_totales() -> int:
    """Devuelve el total de disparos hechos por el jugador e ia"""
    return len(game_state.player_shots) + len(game_state.ai_shots)


def calcular_barcos_restantes(tablero: List[List[int]]) -> int:
    """
    Calcula cuántos barcos quedan a flote en el tablero.
    Un barco se considera a flote si le queda al menos 1 casilla sin destruir.
    """
    # Contadores de casillas encontradas por tamaño/identificador de barco
    conteo_celdas = {tamaño: 0 for tamaño in SHIP_SIZES}

    # Un único recorrido de la matriz
    for fila in tablero:
        for celda in fila:
            if celda in conteo_celdas:
                conteo_celdas[celda] += 1

    # Un barco sigue a flote si el número de casillas encontradas coincide con su tamaño total
    barcos_restantes = sum(
        1 for tamaño in SHIP_SIZES if conteo_celdas[tamaño] == tamaño
    )

    return barcos_restantes
