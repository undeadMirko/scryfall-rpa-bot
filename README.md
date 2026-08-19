# Proyecto 3: Bot de Automatización RPA (Scryfall)

Este proyecto implementa un bot de **Robotic Process Automation (RPA)** utilizando **Python 3.11+ y Selenium WebDriver**. Su propósito es automatizar la búsqueda y extracción de datos de cartas de Magic: The Gathering desde la web de [Scryfall](https://scryfall.com/).

## 🤖 Lógica del Procesamiento y Flujo del Bot

1. **Lectura de Entradas:** El script principal (`src/main.py`) lee un archivo Excel (`data/input_cards.xlsx`) que contiene una columna `Card Name`.
2. **Inicialización del Bot:** Se instancia `ScryfallBot`, el cual configura un Selenium WebDriver en modo *headless*, optimizado para ejecutarse en entornos de contenedores (como Docker Alpine).
3. **Búsqueda e Interacción:** Por cada carta:
   - El bot navega a la URL de búsqueda exacta de Scryfall.
   - Aplica esperas explícitas (`WebDriverWait`) para asegurar que los elementos del DOM (título, set, precio) se hayan cargado.
   - En caso de errores transitorios, se aplica un patrón de **Exponential Backoff** a través de un decorador personalizado (`@retry` en `src/utils.py`).
4. **Lógica Defensiva:** Si ocurre un `TimeoutException` o `WebDriverException`, el bot captura automáticamente una **captura de pantalla** del navegador y la guarda en la carpeta `logs/screenshots/` para su posterior análisis.
5. **Extracción y Guardado:** Los datos extraídos (Nombre, Set, Rareza y Precio en USD) se almacenan en memoria y, al finalizar, se persisten en un nuevo archivo Excel (`data/output_prices.xlsx`) usando `pandas` y `openpyxl`.
6. **Logging:** A lo largo de todo el proceso, se registra la actividad mediante el sistema nativo `logging` de Python. No se utiliza `print()`. Los logs se envían a la consola y a un archivo rotativo (`logs/bot.log`).

## 🛠️ Stack Tecnológico
- Python 3.11+
- Selenium WebDriver (Headless)
- Pandas & OpenPyXL
- python-dotenv (para variables de entorno estrictas)
- Docker (Imagen basada en Alpine Linux)

## 🚀 Guía de Instalación y Ejecución

### Opción 1: Ejecución Local (con entorno virtual)

1. **Clonar o descargar el repositorio**.
2. **Crear y activar el entorno virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar variables de entorno**:
   - Copia `.env.example` a `.env`:
     ```bash
     cp .env.example .env
     ```
   - Ajusta los valores si es necesario.
5. **Asegurar archivo de entrada**:
   - Verifica que exista el archivo `data/input_cards.xlsx` con la columna `Card Name`.
6. **Ejecutar el bot**:
   ```bash
   python src/main.py
   ```

### Opción 2: Ejecución mediante Docker (Desatendida)

Se ha proporcionado un `Dockerfile` basado en `python:3.11-alpine` con Chromium preinstalado.

1. **Construir la imagen de Docker**:
   ```bash
   docker build -t scryfall-rpa-bot .
   ```
2. **Ejecutar el contenedor**:
   Para poder recuperar los resultados (`output_prices.xlsx`) y los logs/capturas de pantalla, es indispensable mapear los volúmenes correspondientes de tu máquina local al contenedor.

   ```bash
   docker run --rm \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     --env-file .env \
     scryfall-rpa-bot
   ```

3. Al finalizar, los resultados estarán en `data/output_prices.xlsx` y los logs en `logs/bot.log`.
