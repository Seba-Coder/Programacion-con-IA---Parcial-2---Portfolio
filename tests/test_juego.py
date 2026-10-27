"""
Suite de pruebas unitarias y de integración para juego.py.
Organizada con el patrón AAA (Arrange, Act, Assert).
"""

import random
import pytest
import juego


# =====================================================================
# 1. GENERACIÓN DE TABLEROS
# =====================================================================
class TestGeneracionTableros:
    def test_generacion_tableros_en_50_semillas(self):
        """
        Verifica a lo largo de 50 semillas distintas que los tableros generados
        contengan 3 barcos de tamaños 3, 2 y 1, dentro del tablero de 6x6,
        sin superponerse ni tocarse ortogonal o diagonalmente.
        """
        for semilla in range(50):
            # Arrange
            random.seed(semilla)

            # Act
            barcos, ocupadas = juego.game_state._generate_board()

            # Assert
            assert len(barcos) == 3, f"Semilla {semilla}: se esperaban 3 barcos, pero hay {len(barcos)}"
            tamanos = sorted([len(b) for b in barcos])
            assert tamanos == [1, 2, 3], f"Semilla {semilla}: los tamaños deben ser [1, 2, 3], se obtuvo {tamanos}"

            # Todas las casillas dentro del tablero de 6x6
            for x, y in ocupadas:
                assert 0 <= x < juego.BOARD_SIZE and 0 <= y < juego.BOARD_SIZE, (
                    f"Semilla {semilla}: coordenada ({x}, {y}) fuera de rango"
                )

            # Ocupadas coincide con la unión de las celdas de los barcos
            union_barcos = set().union(*barcos)
            assert ocupadas == union_barcos, f"Semilla {semilla}: las casillas ocupadas no coinciden con la unión de barcos"

            # Sin superposición ni adyacencia (incluso diagonales) entre barcos distintos
            for i in range(len(barcos)):
                for j in range(i + 1, len(barcos)):
                    barco_a = barcos[i]
                    barco_b = barcos[j]
                    assert barco_a.isdisjoint(barco_b), f"Semilla {semilla}: los barcos {i} y {j} se superponen"

                    for ax, ay in barco_a:
                        for bx, by in barco_b:
                            distancia_chebyshev = max(abs(ax - bx), abs(ay - by))
                            assert distancia_chebyshev > 1, (
                                f"Semilla {semilla}: los barcos {i} y {j} se tocan en ({ax}, {ay}) y ({bx}, {by})"
                            )


# =====================================================================
# 2. RESOLUCIÓN DE DISPAROS DEL JUGADOR (disparar_a_ia)
# =====================================================================
class TestDispararAIA:
    def test_disparo_a_ia_agua(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        coord_agua = (5, 5)

        # Act
        resultado = juego.disparar_a_ia(*coord_agua)

        # Assert
        assert resultado == f"Disparo en ({coord_agua[0]}, {coord_agua[1]}): AGUA."
        assert coord_agua in juego.game_state.player_shots
        assert coord_agua not in juego.game_state.player_hits

    def test_disparo_a_ia_tocado(self, colocar_barcos):
        # Arrange
        datos = colocar_barcos()
        # Barco de tamaño 3 está en (0, 0), (1, 0), (2, 0)
        coord_impacto = (0, 0)

        # Act
        resultado = juego.disparar_a_ia(*coord_impacto)

        # Assert
        assert resultado == f"¡Impacto en ({coord_impacto[0]}, {coord_impacto[1]})! TOCADO."
        assert coord_impacto in juego.game_state.player_shots
        assert coord_impacto in juego.game_state.player_hits

    def test_disparo_a_ia_hundido_con_tamano(self, colocar_barcos):
        # Arrange
        datos = colocar_barcos()
        # Barco de tamaño 1 está en (0, 5)
        coord_barco_1 = (0, 5)

        # Act
        resultado = juego.disparar_a_ia(*coord_barco_1)

        # Assert
        assert "HUNDIDO" in resultado
        assert "tamaño 1" in resultado
        assert resultado == f"¡Impacto en ({coord_barco_1[0]}, {coord_barco_1[1]})! HUNDIDO. Hundiste un barco de la IA de tamaño 1."

        # También verificar barco de tamaño 2: {(4, 2), (4, 3)}
        juego.disparar_a_ia(4, 2)
        resultado_hundido_2 = juego.disparar_a_ia(4, 3)
        assert "HUNDIDO" in resultado_hundido_2
        assert "tamaño 2" in resultado_hundido_2

    def test_disparo_a_ia_coordenadas_fuera_de_rango(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        coordenadas_invalidas = [(-1, 0), (0, -1), (6, 0), (0, 6), (99, 99)]

        for x, y in coordenadas_invalidas:
            # Act
            resultado = juego.disparar_a_ia(x, y)

            # Assert
            assert resultado.startswith("Error:"), f"Se esperaba error para coordenada ({x}, {y}), pero se obtuvo: {resultado}"
            assert (x, y) not in juego.game_state.player_shots

    def test_disparo_a_ia_repetido_sin_duplicar_registro(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        coord = (3, 3)
        juego.disparar_a_ia(*coord)
        total_disparos_inicial = len(juego.game_state.player_shots)

        # Act
        resultado_repetido = juego.disparar_a_ia(*coord)

        # Assert
        assert "Ya habías disparado" in resultado_repetido
        assert len(juego.game_state.player_shots) == total_disparos_inicial


# =====================================================================
# 3. LÓGICA DE DECISIÓN DE DISPARO (decidir_disparo)
# =====================================================================
class TestDecidirDisparo:
    def test_decidir_disparo_toma_primera_de_la_cola(self):
        # Arrange
        ai_shots = set()
        ai_target_queue = [(2, 3), (4, 5)]

        # Act
        decision = juego.decidir_disparo(ai_shots, ai_target_queue, 6)

        # Assert
        assert decision["x"] == 2
        assert decision["y"] == 3
        assert decision["modo"] == "persecucion"

    def test_decidir_disparo_saltea_casillas_ya_disparadas(self):
        # Arrange
        ai_shots = {(2, 3)}
        ai_target_queue = [(2, 3), (4, 5)]

        # Act
        decision = juego.decidir_disparo(ai_shots, ai_target_queue, 6)

        # Assert
        assert decision["x"] == 4
        assert decision["y"] == 5
        assert decision["modo"] == "persecucion"

    def test_decidir_disparo_caza_reproducible_con_rng(self):
        # Arrange
        ai_shots = {(0, 0), (1, 1)}
        ai_target_queue = []
        rng1 = random.Random(42)
        rng2 = random.Random(42)

        # Act
        dec1 = juego.decidir_disparo(ai_shots, ai_target_queue, 6, rng=rng1)
        dec2 = juego.decidir_disparo(ai_shots, ai_target_queue, 6, rng=rng2)

        # Assert
        assert dec1["modo"] == "caza"
        assert dec2["modo"] == "caza"
        assert dec1 == dec2

    def test_decidir_disparo_lanza_value_error_sin_casillas(self):
        # Arrange
        todas_las_casillas = {(x, y) for x in range(6) for y in range(6)}
        ai_target_queue = []

        # Act & Assert
        with pytest.raises(ValueError, match="No quedan casillas disponibles"):
            juego.decidir_disparo(todas_las_casillas, ai_target_queue, 6)

    def test_decidir_disparo_no_modifica_sus_argumentos(self):
        # Arrange
        ai_shots = {(1, 1), (2, 2)}
        ai_target_queue = [(1, 1), (3, 3)]
        shots_copia = set(ai_shots)
        queue_copia = list(ai_target_queue)

        # Act
        juego.decidir_disparo(ai_shots, ai_target_queue, 6)

        # Assert
        assert ai_shots == shots_copia, "ai_shots fue modificado por decidir_disparo"
        assert ai_target_queue == queue_copia, "ai_target_queue fue modificado por decidir_disparo"

    def test_decidir_disparo_nunca_repite_casilla(self):
        # Arrange
        ai_shots = set()
        ai_target_queue = []
        total_casillas = 6 * 6

        # Act & Assert
        for _ in range(total_casillas):
            decision = juego.decidir_disparo(ai_shots, ai_target_queue, 6)
            coord = (decision["x"], decision["y"])
            assert coord not in ai_shots, f"Se devolvió una coordenada ya disparada: {coord}"
            ai_shots.add(coord)

        assert len(ai_shots) == total_casillas


# =====================================================================
# 4. EJECUCIÓN DE DISPAROS DE LA IA (ejecutar_disparo_ia)
# =====================================================================
class TestEjecutarDisparoIA:
    def test_ejecutar_disparo_ia_agua(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        coord_agua = (5, 5)

        # Act
        resultado = juego.ejecutar_disparo_ia(*coord_agua)

        # Assert
        assert resultado == f"La IA disparó en ({coord_agua[0]}, {coord_agua[1]}): AGUA."
        assert coord_agua in juego.game_state.ai_shots
        assert coord_agua not in juego.game_state.ai_hits

    def test_ejecutar_disparo_ia_tocado_agrega_solo_vecinas_validas_esquina(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # Barco de tamaño 3 está en (0, 0), (1, 0), (2, 0)
        # (0, 0) está en la esquina del tablero; sus únicas vecinas válidas son (1, 0) y (0, 1)
        coord_esquina = (0, 0)

        # Act
        resultado = juego.ejecutar_disparo_ia(*coord_esquina)

        # Assert
        assert "TOCADO" in resultado
        assert juego.game_state.ai_mode == "persecucion"
        assert set(juego.game_state.ai_target_queue) == {(1, 0), (0, 1)}
        # No debe contener coordenadas fuera de límites
        for vx, vy in juego.game_state.ai_target_queue:
            assert 0 <= vx < 6 and 0 <= vy < 6

    def test_ejecutar_disparo_ia_hundido_vacia_cola(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # Barco de tamaño 1 está en (0, 5)
        coord_barco_1 = (0, 5)
        juego.game_state.ai_target_queue = [(2, 2), (3, 3)]
        juego.game_state.ai_mode = "persecucion"

        # Act
        resultado = juego.ejecutar_disparo_ia(*coord_barco_1)

        # Assert
        assert "HUNDIDO" in resultado
        assert "tamaño 1" in resultado
        assert juego.game_state.ai_mode == "caza"
        assert len(juego.game_state.ai_target_queue) == 0


# =====================================================================
# 5. VERIFICACIÓN DE FIN DE JUEGO
# =====================================================================
class TestVerificarFinJuego:
    def test_verificar_fin_juego_partida_en_curso(self, colocar_barcos):
        # Arrange
        colocar_barcos()

        # Act
        resultado = juego.verificar_fin_juego()

        # Assert
        assert resultado == "La partida continúa. Aún hay barcos a flote en ambos lados."

    def test_verificar_fin_juego_gana_jugador(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # El jugador impactó todas las casillas de los barcos de la IA
        juego.game_state.player_hits = set(juego.game_state.ai_ship_coords)

        # Act
        resultado = juego.verificar_fin_juego()

        # Assert
        assert "¡Ganaste la partida!" in resultado

    def test_verificar_fin_juego_gana_ia(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # La IA impactó todas las casillas de los barcos del jugador
        juego.game_state.ai_hits = set(juego.game_state.player_ship_coords)

        # Act
        resultado = juego.verificar_fin_juego()

        # Assert
        assert "¡La IA ganó la partida!" in resultado

    def test_verificar_fin_juego_empate(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # Ambos completaron los impactos al mismo tiempo
        juego.game_state.player_hits = set(juego.game_state.ai_ship_coords)
        juego.game_state.ai_hits = set(juego.game_state.player_ship_coords)

        # Act
        resultado = juego.verificar_fin_juego()

        # Assert
        assert "¡Empate!" in resultado


# =====================================================================
# 6. ESTADO DE LA PARTIDA (obtener_estado_partida)
# =====================================================================
class TestObtenerEstadoPartida:
    def test_obtener_estado_partida_muestra_disparos_ia_en_tablero_jugador_y_no_del_jugador(self, colocar_barcos):
        """
        El tablero_jugador debe mostrar los disparos realizados por la IA
        ('O' en agua, 'X' en impacto) y NO los disparos del jugador humano.
        El tablero_ia_descubierto debe mostrar los disparos del jugador.
        """
        # Arrange
        colocar_barcos()

        # El jugador dispara a la IA en agua (5, 5) y en impacto (0, 5)
        juego.game_state.player_shots = {(5, 5), (0, 5)}
        juego.game_state.player_hits = {(0, 5)}

        # La IA dispara al jugador en agua (3, 3) y en impacto (0, 0)
        juego.game_state.ai_shots = {(3, 3), (0, 0)}
        juego.game_state.ai_hits = {(0, 0)}

        # Act
        estado = juego.obtener_estado_partida()
        grid_jugador = [fila.split() for fila in estado["tablero_jugador"]]
        grid_ia = [fila.split() for fila in estado["tablero_ia_descubierto"]]

        # Assert
        # 1. En tablero_jugador: la IA disparó en (3, 3) al agua -> 'O'
        assert grid_jugador[3][3] == "O", (
            f"tablero_jugador en (3, 3) debería ser 'O' por disparo de agua de la IA, pero fue '{grid_jugador[3][3]}'"
        )

        # 2. En tablero_jugador: la IA disparó en (0, 0) a un barco -> 'X'
        assert grid_jugador[0][0] == "X", (
            f"tablero_jugador en (0, 0) debería ser 'X' por impacto de la IA, pero fue '{grid_jugador[0][0]}'"
        )

        # 3. En tablero_jugador: (5, 5) NO fue disparado por la IA -> debe ser '~', no 'O'
        assert grid_jugador[5][5] != "O", (
            "tablero_jugador no debe mostrar los disparos hechos por el jugador (5, 5)"
        )

        # 4. En tablero_ia_descubierto: el jugador disparó en (5, 5) -> 'O'
        assert grid_ia[5][5] == "O", (
            f"tablero_ia_descubierto en (5, 5) debería ser 'O' por disparo del jugador, pero fue '{grid_ia[5][5]}'"
        )

        # 5. En tablero_ia_descubierto: el jugador disparó en (0, 5) -> 'X'
        assert grid_ia[5][0] == "X", (
            f"tablero_ia_descubierto en (0, 5) debería ser 'X' por impacto del jugador, pero fue '{grid_ia[5][0]}'"
        )


# =====================================================================
# 7. FIN DE PARTIDA: BLOQUEO DE DISPAROS TRAS TERMINAR
# =====================================================================
class TestFinDePartida:
    def test_disparar_a_ia_bloqueado_tras_fin_de_partida(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # Partida ganada por el jugador
        juego.game_state.player_hits = set(juego.game_state.ai_ship_coords)
        disparos_antes = len(juego.game_state.player_shots)

        # Act
        resultado = juego.disparar_a_ia(1, 1)

        # Assert
        assert resultado.startswith("Error:"), (
            f"disparar_a_ia debería devolver un mensaje con 'Error:' una vez terminada la partida, pero devolvió: {resultado}"
        )
        assert len(juego.game_state.player_shots) == disparos_antes, (
            "No se debe registrar el disparo tras el fin de la partida"
        )

    def test_ejecutar_disparo_ia_bloqueado_tras_fin_de_partida(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # Partida ganada por la IA
        juego.game_state.ai_hits = set(juego.game_state.player_ship_coords)
        disparos_antes = len(juego.game_state.ai_shots)

        # Act
        resultado = juego.ejecutar_disparo_ia(1, 1)

        # Assert
        assert resultado.startswith("Error:"), (
            f"ejecutar_disparo_ia debería devolver un mensaje con 'Error:' una vez terminada la partida, pero devolvió: {resultado}"
        )
        assert len(juego.game_state.ai_shots) == disparos_antes, (
            "No se debe registrar el disparo de la IA tras el fin de la partida"
        )

    def test_disparar_a_jugador_bloqueado_tras_fin_de_partida(self, colocar_barcos):
        # Arrange
        colocar_barcos()
        # Partida ganada por el jugador
        juego.game_state.player_hits = set(juego.game_state.ai_ship_coords)
        disparos_antes = len(juego.game_state.ai_shots)

        # Act
        resultado = juego.disparar_a_jugador()

        # Assert
        assert resultado.startswith("Error:"), (
            f"disparar_a_jugador debería devolver un mensaje con 'Error:' una vez terminada la partida, pero devolvió: {resultado}"
        )
        assert len(juego.game_state.ai_shots) == disparos_antes, (
            "No se debe ejecutar ni registrar el disparo automático tras el fin de la partida"
        )


# =====================================================================
# 8. CÁLCULO DE BARCOS RESTANTES (calcular_barcos_restantes)
# =====================================================================
class TestCalcularBarcosRestantes:
    def test_calcular_barcos_restantes_con_barco_parcialmente_danado(self):
        """
        Según el docstring de calcular_barcos_restantes:
        'Un barco se considera a flote si le queda al menos 1 casilla sin destruir.'
        Si un barco de tamaño 3 tiene 2 casillas restantes (1 dañada),
        debe contar como barco a flote.
        """
        # Arrange
        # Tablero 6x6 vacío (0)
        tablero = [[0 for _ in range(juego.BOARD_SIZE)] for _ in range(juego.BOARD_SIZE)]

        # Barco de tamaño 3 parcialmente dañado: solo 2 casillas presentes
        tablero[0][0] = 3
        tablero[0][1] = 3
        # La tercera casilla (0, 2) fue destruida (permanece en 0)

        # Barco de tamaño 2 completamente intacto: 2 casillas
        tablero[2][0] = 2
        tablero[2][1] = 2

        # Barco de tamaño 1 totalmente destruido: 0 casillas presentes

        # Act
        restantes = juego.calcular_barcos_restantes(tablero)

        # Assert
        # Debe contar 2 barcos a flote: el de tamaño 3 (2 celdas >= 1) y el de tamaño 2 (2 celdas >= 1)
        assert restantes == 2, (
            f"Se esperaban 2 barcos a flote (el de 3 con 2 casillas y el de 2 intacto), pero la función devolvió {restantes}"
        )
