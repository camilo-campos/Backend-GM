from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import joblib
import pandas as pd
import json
import datetime  # Para obtener la hora de ejecución

router = APIRouter()

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del archivo actual
MODELS_DIR = os.path.join(BASE_DIR, "..", "modelos_prediccion")  # Ruta absoluta a la carpeta de modelos

modelos = {
    "corriente_motor": joblib.load(os.path.join(MODELS_DIR, "model_Corriente Motor Bomba Agua Alimentacion BFWP A (A).pkl")),
    
    "presion_agua": joblib.load(os.path.join(MODELS_DIR, "model_Presión Agua Alimentación AP (barg).pkl")),
    "salida_bomba": joblib.load(os.path.join(MODELS_DIR, "model_Salida de Bomba de Alta Presión.pkl")),
    
}


def predecir_sensores(datos, modelo):
    # Convierte los datos en un DataFrame
    df_nuevo = pd.DataFrame(datos, columns=["valor"])
    # Aplica la predicción y retorna la lista resultante
    return modelo.predict(df_nuevo).tolist()

# Clase para manejar conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            modelo_key = request.get("modelo")  # Selecciona el modelo
            datos = request.get("datos")         # Lista de datos de sensores
            tiempos = request.get("tiempos")       # Lista de tiempos asociados a cada dato

            if modelo_key in modelos and datos and tiempos:
                # Se ejecuta la predicción
                predicciones = predecir_sensores(datos, modelos[modelo_key])
                # Se obtiene el tiempo de ejecución (por ejemplo, la hora actual en formato HH:MM)
                tiempo_ejecucion = datetime.datetime.now().strftime("%H:%M")
                # Se crea la respuesta con los datos, el tiempo de ejecución y las predicciones.
                response = {
                    "tiempo_ejecucion": tiempo_ejecucion,
                    "datos": datos,
                    "tiempos_recibidos": tiempos,
                    "prediccion": predicciones,
                }
                await manager.send_message(json.dumps(response))
            else:
                await manager.send_message(json.dumps({"error": "Modelo no encontrado o datos inválidos"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
