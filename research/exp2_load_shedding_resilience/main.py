import asyncio
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configuramos el limitador usando la IP del cliente como llave
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
# Acoplamos el limitador a la aplicación
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/buscar")
@limiter.limit("50/minute") # Límite estricto para forzar el rechazo rápido
async def buscar_hoteles(request: Request):
    # Simulamos el tiempo de I/O en la base de datos de una búsqueda real
    await asyncio.sleep(0.5) 
    return {"status": "success", "mensaje": "Hospedajes encontrados"}