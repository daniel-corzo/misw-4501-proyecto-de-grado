import os
import asyncio
from fastapi import FastAPI

app = FastAPI()

# Obtenemos el ID único del contenedor de Docker
CONTAINER_ID = os.getenv("HOSTNAME", "local")

@app.post("/reservas")
async def crear_reserva():
    # Simulamos el tiempo de procesamiento de una reserva (200ms)
    await asyncio.sleep(0.2)
    return {
        "status": "success", 
        "mensaje": "Reserva confirmada", 
        "procesado_por": CONTAINER_ID
    }