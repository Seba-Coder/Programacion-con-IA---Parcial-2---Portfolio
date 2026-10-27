"""
Script de consola para jugar Batalla Naval contra la IA con narración del Capitán.
"""

import sys
import json
import random
import argparse

import juego
import agente


def parse_args():
    parser = argparse.ArgumentParser(
        description="Jugar Batalla Naval contra la IA con narración del Capitán."
    )
    parser.add_argument(
        "--semilla",
        type=int,
        default=None,
        help="Semilla aleatoria para inicializar el generador (demo reproducible)."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Fijar semilla opcional para reproducibilidad
    if args.semilla is not None:
        random.seed(args.semilla)
        print(f"Semilla fijada en: {args.semilla}")

    # Inicialización del juego y carga del agente
    print("Iniciando partida...")
    msg_inicio = juego.iniciar_partida()
    print(msg_inicio)

    print("Cargando agente Capitán...")
    agente_cargado = agente.cargar_agente()
    print(f"Agente listo: {agente_cargado['name']} ({agente_cargado['model']})")
    print("=" * 50)
    print("¡Comienza la partida! Indicá tus disparos como 'x y' (0 a 5).")
    print("=" * 50)

    # Bucle principal del juego
    while True:
        # 1. Pedir disparo al jugador y validar entrada
        try:
            entrada = input("\nIngresá tu disparo (formato 'x y', ej. '2 3') o 'q' para salir: ").strip()
            if entrada.lower() == "q":
                print("Partida terminada por el jugador.")
                break

            partes = entrada.split()
            if len(partes) != 2:
                print("Entrada no válida: ingresá exactamente 2 números separados por espacio.")
                continue

            x, y = int(partes[0]), int(partes[1])
        except ValueError:
            print("Entrada no válida: asegurate de ingresar números enteros.")
            continue
        except (KeyboardInterrupt, EOFError):
            print("\nPartida cancelada.")
            break

        # 2. Ejecutar disparo del jugador a la IA y mostrar resultado
        res_jugador = juego.disparar_a_ia(x, y)
        print(f"\nResultado de tu disparo: {res_jugador}")

        # Si hubo error de rango o casilla repetida, permitir reintentar sin ceder el turno
        if res_jugador.startswith("Error:") or res_jugador.startswith("Ya habías"):
            continue

        # 3. Verificar fin de juego tras el disparo del jugador
        fin_msg = juego.verificar_fin_juego()
        if "Ganaste" in fin_msg or "La IA ganó" in fin_msg or "Empate" in fin_msg:
            print(f"\n¡Fin de la partida! {fin_msg}")
            break

        # 4. Turno de la IA
        print("\n" + "-" * 30)
        print("TURNO DE LA IA:")
        try:
            decision = juego.decidir_disparo(
                ai_shots=juego.game_state.ai_shots,
                ai_target_queue=juego.game_state.ai_target_queue,
                board_size=juego.BOARD_SIZE
            )
        except ValueError:
            print("La IA no tiene casillas disponibles para disparar.")
            fin_msg = juego.verificar_fin_juego()
            print(f"\n¡Fin de la partida! {fin_msg}")
            break

        print("[Skill Puntería] Decisión JSON:")
        print(json.dumps(decision, indent=2, ensure_ascii=False))

        # Narración del Capitán
        narracion = agente.narrar_disparo(decision, agente_cargado)
        print(f"\nCapitán: {narracion}")

        # Ejecución del disparo de la IA
        res_ia = juego.ejecutar_disparo_ia(decision["x"], decision["y"])
        print(f"Resultado del disparo de la IA: {res_ia}")

        # 5. Verificar fin de juego tras el disparo de la IA
        fin_msg = juego.verificar_fin_juego()
        if "Ganaste" in fin_msg or "La IA ganó" in fin_msg or "Empate" in fin_msg:
            print(f"\n¡Fin de la partida! {fin_msg}")
            break


if __name__ == "__main__":
    main()
