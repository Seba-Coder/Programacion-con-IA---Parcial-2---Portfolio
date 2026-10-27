# Batalla Naval con Agente Narrador e Integración MCP (Parcial 2)

Proyecto de **Batalla Naval** en Python sobre un tablero de 6×6 casillas con 3 barcos (tamaños 3, 2 y 1). El sistema combina lógica determinista clásica (*Hunt-and-Target*), una capa generativa con el **Agente Capitán** (ejecutado con `llama3.1:8b` sobre Ollama) que narra los disparos en personaje, y una interfaz de **Servidor MCP** (`FastMCP`) para integración con clientes y asistentes basados en el Model Context Protocol.

Para un análisis detallado del diseño del sistema, diagramas Mermaid de flujo y justificación de decisiones, consultá la [Documentación de Arquitectura (docs/arquitectura.md)](docs/arquitectura.md).

---

## 🚀 Requisitos del Sistema

- **Python**: 3.10 o superior (probado y verificado en Python 3.11.9).
- **Ollama**: Instalado localmente y en ejecución en su puerto por defecto (`http://localhost:11434`).
- **Modelo LLM**: `llama3.1:8b` descargado en Ollama.

---

## 📦 Instalación Paso a Paso

1. **Clonar o ubicarse en la raíz del repositorio**:
   ```bash
   cd "Parcial 2"
   ```

2. **Crear y activar el entorno virtual**:
   - En Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - En Windows (CMD):
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate.bat
     ```
   - En Linux / macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Instalar dependencias del proyecto**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Instala `mcp<2`, `pytest` y `ollama`).*

4. **Descargar el modelo local en Ollama**:
   Asegurate de que el servicio de Ollama esté iniciado y ejecutá:
   ```bash
   ollama pull llama3.1:8b
   ```

---

## 🎮 Cómo Jugar en Consola (`jugar.py`)

El modo interactivo en consola permite jugar una partida por turnos contra la IA con narración del Capitán y visualización de ambos tableros con niebla de guerra:

```bash
python jugar.py
```

### Partidas reproducibles con semilla
Para demostraciones o pruebas donde se requiera que la disposición inicial de barcos y las decisiones aleatorias sean deterministas, se puede especificar la opción `--semilla`:

```bash
python jugar.py --semilla 42
```

### Dinámica del juego:
1. Al inicio de cada turno se imprime tu tablero completo (con tus barcos `B`, impactos de la IA `X` y agua disparada `O`) y el tablero de la IA descubierto (solo impactos `X` y disparos fallidos `O`).
2. Ingresá tus coordenadas en formato `x y` (columna fila, de 0 a 5) o escribí `q` para abandonar.
3. La IA ejecuta su turno: la **Skill de Puntería** decide el objetivo táctico, el **Capitán** narra el disparo en personaje y se aplica el resultado en tu tablero.

---

## 🔌 Servidor MCP y Cliente de Prueba

### Ejecución del Servidor MCP
El servidor expone herramientas y recursos para interactuar con el juego a través de FastMCP por entrada/salida estándar:

```bash
python battleship.py
```

### Cliente de prueba standalone
Podés probar las herramientas y recursos del servidor MCP de forma interactiva y local sin requerir un cliente MCP externo complejo:

```bash
python test_client.py
```

### Configuración en Antigravity / Clientes MCP
Para conectar el servidor MCP a Antigravity IDE u otros clientes compatibles, agregá la configuración correspondiente en tu `mcp_config.json`:

* **Ubicación típica en Antigravity**: `C:\Users\<Usuario>\.gemini\config\mcp_config.json`

```json
{
  "mcpServers": {
    "battleship-mcp": {
      "command": "c:\\Users\\Seba\\Desktop\\Sebastian\\Universidad\\Programación con IA generativa (Electiva 1)\\Parcial 2\\.venv\\Scripts\\python.exe",
      "args": [
        "c:\\Users\\Seba\\Desktop\\Sebastian\\Universidad\\Programación con IA generativa (Electiva 1)\\Parcial 2\\battleship.py"
      ]
    }
  }
}
```

---

## 🧪 Ejecución de Pruebas (`pytest`)

El proyecto cuenta con una suite completa de 35 pruebas automatizadas estructuradas con el patrón AAA (*Arrange-Act-Assert*):

1. **Ejecutar toda la suite de pruebas**:
   ```bash
   python -m pytest -v
   ```

2. **Ejecutar únicamente las pruebas con el modelo real Ollama**:
   ```bash
   python -m pytest -m ollama -v -s
   ```

3. **Ejecutar solo las pruebas rápidas / deterministas (sin invocar al modelo real)**:
   ```bash
   python -m pytest -m "not ollama" -v
   ```

---

## ⚓ El Agente y la Skill

El sistema separa con precisión la lógica táctica determinista de la interpretación artística:

- **El Agente Capitán** ([prompts_agentes/capitan.agent.md](prompts_agentes/capitan.agent.md)):  
  Define la personalidad de un capitán de la flota que narra en personaje las decisiones de disparo. El archivo combina un frontmatter YAML con los metadatos del agente (`name`, `model`, `description`) y el cuerpo Markdown con el prompt de sistema. Su misión es exclusivamente narrar las decisiones tácticas de la IA, manteniéndose en personaje e incluyendo de forma obligatoria las coordenadas `(x, y)`.
- **La Skill de Puntería** ([skills/skill-punteria.md](skills/skill-punteria.md)):  
  Documenta el contrato de entrada y salida del autómata de estados *Hunt-and-Target*. La función `juego.decidir_disparo` implementa esta skill: en modo caza busca casillas libres al azar y en modo persecución extrae casillas contiguas tras un impacto previo, devolviendo un JSON estructurado con `x`, `y`, `modo` y `motivo`.

---

## 🧠 Parámetros del Modelo y Configuración

En [agente.py](agente.py) se definen los parámetros de inferencia utilizados para interactuar con la API local de Ollama:

| Parámetro | Valor | Justificación Técnica |
| :--- | :--- | :--- |
| **Modelo** | `llama3.1:8b` | Modelo local que corre completo en GPU. Sigue bien instrucciones en español, pero requirió reforzar las restricciones de rol en el .md (ver docs/arquitectura.md, sección 5.3). |
| **`TEMPERATURA`** | `0.3` | Temperatura baja y conservadora que reduce la variabilidad estocástica, asegurando consistencia estilística y el cumplimiento estricto del formato de coordenadas `(x, y)`. |
| **`NUM_CTX`** | `4096` | Tamaño de ventana de contexto suficiente para abarcar el prompt de sistema completo del Capitán y los mensajes del turno sin riesgo de truncamiento. |
| **Control de Reintentos** | 3 intentos en total | `narrar_disparo` verifica que la narración contenga el texto exacto `(x, y)`. Si no, reintenta hasta 2 veces más y, si sigue fallando, devuelve un mensaje de respaldo fijo con las coordenadas correctas. |

---

## 📂 Estructura del Proyecto

```
Parcial 2/
├── prompts_agentes/
│   └── capitan.agent.md       # Definición del Agente Capitán (frontmatter YAML + prompt)
├── skills/
│   └── skill-punteria.md      # Especificación y contrato de la Skill de Puntería
├── docs/
│   └── arquitectura.md        # Documentación de arquitectura, diagramas y decisiones de diseño
├── tests/
│   ├── test_juego.py          # Pruebas unitarias de la lógica del juego (24 tests)
│   └── test_agente.py         # Pruebas del agente con mock y modelo real (11 tests)
├── conftest.py                # Fixtures de pytest y helper determinista colocar_barcos()
├── pytest.ini                 # Configuración de pytest y registro del marcador 'ollama'
├── juego.py                   # Lógica pura del juego, GameState y algoritmo Hunt-and-Target
├── agente.py                  # Cliente de Ollama, carga de prompts, reintentos y narración
├── jugar.py                   # Bucle interactivo por turnos en consola con narración
├── battleship.py              # Servidor MCP (FastMCP) con tools y resource
├── test_client.py             # Cliente de prueba standalone para el servidor MCP
├── requirements.txt           # Dependencias del proyecto (mcp, pytest, ollama)
└── README.md                  # Documentación principal del proyecto
```