# ExaBOT

Bot de Discord para el espacio de Discord [ExactasDs](https://dsc.gg/exactasds)
programado en Python usando
[PyCord](https://github.com/Pycord-Development/pycord) y
[MongoDB](https://www.mongodb.com/).

Monitoreo: <https://exabot.betteruptime.com>

## Características

- Bienvenidas y despedidas personalizables.
- Reacciones automáticas.

El desarrollo de nuevas funciones se puede seguir [aquí](https://github.com/users/CrysoK/projects/2).

## Requisitos

- Python 3.8 o superior
- Base de datos MongoDB
- Token de un bot de Discord

## Instalación

1. Clonar el repositorio

    ```bash
    git clone https://github.com/CrysoK/ExaBOT
    cd ExaBOT

2. Crear un "entorno virtual" (opcional)

    ```bash
    python -m venv .venv
    # activarlo en Linux
    source .venv/bin/activate
    # activarlo en Windows (cmd)
    .venv\Scripts\activate
    # activarlo en Windows (powershell)
    .venv/Scripts/Activate.ps1
    ```

3. Instalar dependencias

    ```bash
    pip install -r requirements.txt
    ```

4. Define las siguientes variables de entorno (puede usarse un archivo `.env`):
    - `BOT_TOKEN`: El token del bot de Discord.
    - `MONGODB_URI`: La URI de conexión a la base de datos MongoDB.
    - `DB_NAME`: El nombre de la base de datos.
    - `HEARTBEAT_URL`: La URL para enviar heartbeats.
    - `DEBUG_GUILDS`: (Opcional) Lista de IDs separados por coma de espacios de
      Discord donde se registrarán los comandos durante el desarrollo.
    - `LOG_LEVEL`: (Opcional) Nivel de registro. Por defecto `INFO`.
    - `NO_TIMESTAMPS`: (Opcional) No mostrar los timestamps en los logs. Si la
      variable está definida (con cualquier valor) se interpreta como `True`.

5. Iniciar el bot:

    ```bash
    python bot.py
    ```

## Contribución

Los estudiantes de Exactas están especialmente invitados a contribuir. Es una
buena oportunidad para practicar Python y la colaboración a través de GitHub. Un
buen punto de partida es elegir alguna de las propuestas pendientes del
[proyecto](https://github.com/users/CrysoK/projects/2) y comentar tus planes en
[ExactasDs](https://dsc.gg/exactasds) (para evitar trabajo repetido). *No es
necesario ser un experto, la idea es aprender*.
