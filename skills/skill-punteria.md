---
name: skill-punteria
description: Contrato in/out y especificación de reglas de decisión para determinar el próximo disparo de la IA en Batalla Naval.
---

# Skill: Puntería de la IA (Hunt-and-Target)

## Objetivo
Calcular y decidir de forma aislada y determinista las coordenadas del próximo disparo de la IA sobre el tablero del jugador humano, desacoplando la lógica de selección estratégica respecto de la ejecución efectiva del disparo y de la mutación del estado del juego.

---

## Inputs (con tipos)
La función de decisión recibe los siguientes parámetros:

- **`ai_shots`** (`Set[Tuple[int, int]]` o `Collection[Tuple[int, int]]`): Conjunto de coordenadas `(x, y)` donde la IA ya ha realizado disparos con anterioridad.
- **`ai_target_queue`** (`List[Tuple[int, int]]`): Cola ordenada de casillas prioritarias pendientes por explorar, generadas tras registrar un impacto previo (*modo persecución*).
- **`board_size`** (`int`): Dimensión del lado del tablero cuadrado (N x N, típicamente `6` para coordenadas de `0` a `5`).
- **`rng`** (`Optional[random.Random]`, por defecto `None`): Instancia opcional de generador pseudoaleatorio para garantizar reproducibilidad en pruebas y simulaciones. Si se omite, se emplea el módulo global `random`.

---

## Outputs (el JSON exacto de decidir_disparo)
La función retorna un diccionario Python representable como el siguiente JSON exacto:

```json
{
  "x": 0,
  "y": 0,
  "modo": "caza",
  "motivo": "Disparo aleatorio en modo caza"
}
```

### Esquema de campos:
| Campo | Tipo | Valores posibles | Descripción |
|---|---|---|---|
| `x` | `int` | `0` a `board_size - 1` | Coordenada horizontal (columna) elegida para el tiro. |
| `y` | `int` | `0` a `board_size - 1` | Coordenada vertical (fila) elegida para el tiro. |
| `modo` | `str` | `"caza"` \| `"persecucion"` | Estrategia activa bajo la cual se seleccionó la coordenada. |
| `motivo` | `str` | Cadena explicativa | Razón por la que se tomó la decisión. |

---

## Reglas de decisión

1. **Prioridad Persecución (*Target*)**:
   - Se examina la lista `ai_target_queue` elemento por elemento en orden secuencial (FIFO).
   - Si se encuentra una casilla `(x, y)` que **no** pertenezca a `ai_shots`, se toma de inmediato como objetivo.
   - En este caso, la decisión se emite con:
     - `modo`: `"persecucion"`
     - `motivo`: `"Objetivo pendiente en cola de persecución"`

2. **Modo Caza (*Hunt*)**:
   - Si `ai_target_queue` está vacía o todas sus casillas ya fueron disparadas previamente, se cambia a modo caza.
   - Se genera la lista de todas las casillas disponibles del tablero:
     todas las casillas con 0 ≤ x, y < board_size que no estén en ai_shots
   - Si no quedan casillas libres (`len(untried) == 0`), se lanza un error `ValueError("No quedan casillas disponibles para disparar.")`.
   - Si hay casillas libres, se selecciona una al azar utilizando `rng.choice(untried)` o `random.choice(untried)`.
   - La decisión se emite con:
     - `modo`: `"caza"`
     - `motivo`: `"Disparo aleatorio en modo caza"`

---

## Restricciones

- **Determinismo**: Dado el mismo conjunto de `ai_shots`, `ai_target_queue`, `board_size` y una instancia de `rng` inicializada con una semilla fija, el resultado siempre será exactamente el mismo.
- **No ejecuta el disparo**: La función no aplica el disparo contra ningún tablero ni resuelve si el tiro resultó en *agua*, *tocado* o *hundido*.
- **No modifica el estado**: Es una función de sólo lectura respecto a sus argumentos. `ai_shots` permanece inalterado y `ai_target_queue` no es modificada ni vaciada.
- **No inventa coordenadas**: Toda coordenada devuelta respeta estrictamente los límites válidos del tablero (0 <= x < board_size) y garantiza no haber sido disparada previamente (no pertenece a ai_shots).

---

## Ejemplos reales de ejecución

### Ejemplo 1: Modo Caza (con semilla fija `rng`)
Se consulta un disparo sin objetivos pendientes en la cola, utilizando un generador `random.Random(42)` sobre un tablero de 6 x 6:

#### Inputs:
```python
ai_shots = {(0, 0), (1, 1), (2, 2)}
ai_target_queue = []
board_size = 6
rng = random.Random(42)
```

#### Invocación:
```python
decidir_disparo(ai_shots, ai_target_queue, board_size, rng=rng)
```

#### Output (JSON exacto):
```json
{
  "x": 1,
  "y": 3,
  "modo": "caza",
  "motivo": "Disparo aleatorio en modo caza"
}
```

---

### Ejemplo 2: Modo Persecución
Tras un impacto previo en `(2, 4)`, la cola contiene objetivos adyacentes. La primera casilla `(2, 3)` ya fue disparada previamente, por lo que la función selecciona la primera celda no disparada `(2, 5)`:

#### Inputs:
```python
ai_shots = {(2, 4), (3, 4)}
ai_target_queue = [(3, 4), (1, 4), (2, 5), (2, 3)]
board_size = 6
rng = None
```

#### Invocación:
```python
decidir_disparo(ai_shots, ai_target_queue, board_size)
```

#### Output (JSON exacto):
```json
{
  "x": 2,
  "y": 5,
  "modo": "persecucion",
  "motivo": "Objetivo pendiente en cola de persecución"
}
```
