# FastAPI Dashboard Backend

## Descripción
Este proyecto es un backend desarrollado con **FastAPI** que proporciona datos en tiempo real para un tablero **dashboard**. La aplicación se encarga de recibir, procesar y transmitir los datos mediante **WebSockets**, permitiendo una actualización en vivo de los gráficos en el frontend.

## Características
- API REST desarrollada con **FastAPI**.
- Soporte para **WebSockets** para la transmisión de datos en tiempo real.
- Integración con modelos de análisis como **IsolationForest** para detectar outliers.
- Conexión a una base de datos para obtener datos de sensores.
- Middleware **CORS** habilitado para permitir peticiones desde el frontend.

## Tecnologías Utilizadas
- **Python 3.10+**
- **FastAPI** (Framework principal)
- **SQLAlchemy** (ORM para la base de datos)
- **WebSockets** (Para comunicación en tiempo real)
- **Scikit-learn** (Para modelos de análisis de datos)

## Instalación
### Prerrequisitos
- Python 3.10 o superior
- pip instalado
- Virtualenv (opcional pero recomendado)

### Pasos de Instalación
1. Clonar el repositorio:
   ```sh
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```
2. Crear y activar un entorno virtual (opcional):
   ```sh
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```
3. Instalar las dependencias:
   ```sh
   pip install -r requirements.txt
   ```
4. Configurar variables de entorno:
   ```sh
   cp .env.example .env
   # Edita el archivo .env con los valores necesarios
   ```
5. Ejecutar la aplicación:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Uso de la API
### Endpoints Principales
| Método  | Ruta         | Descripción |
|----------|-------------|-------------|
| `GET`    | `/data`     | Obtiene los últimos datos de sensores |
| `WS`     | `/ws`       | Conexión WebSocket para datos en tiempo real |

### Ejemplo de Conexión WebSocket
```python
import websockets
import asyncio
import json

async def receive_data():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print("Datos recibidos:", data)

asyncio.run(receive_data())
```

## Contribución
1. Hacer un fork del repositorio
2. Crear una nueva rama (`feature/nueva_funcionalidad`)
3. Hacer commit de los cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Subir la rama (`git push origin feature/nueva_funcionalidad`)
5. Abrir un Pull Request

## Licencia
Este proyecto está bajo la licencia **MIT**.

