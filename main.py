from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar e incluir los routers
from rutas import Corriente_Motor_Bomba_Agua_Alimentacion_BFWP_A , Flujo_de_Agua_Atemperación_Vapor_Alta_AP_SH , Presión_Agua_Alimentación_AP , Salida_de_Bomba_de_Alta_Presión , Vibración_Axial_Descanso_Emp_Bomba_1A 


app.include_router(Corriente_Motor_Bomba_Agua_Alimentacion_BFWP_A.router)
app.include_router(Flujo_de_Agua_Atemperación_Vapor_Alta_AP_SH.router)
app.include_router(Vibración_Axial_Descanso_Emp_Bomba_1A.router)
app.include_router(Presión_Agua_Alimentación_AP.router)
app.include_router(Salida_de_Bomba_de_Alta_Presión.router)
#app.include_router(.router)
#app.include_router(.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}