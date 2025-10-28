from fastapi import FastAPI
from fastapi.responses import Response
from . import clientes_api, productos_api, ventas_api

app = FastAPI(title="API Tienda de Ropa", version="1.0")

# Incluir routers
app.include_router(clientes_api.router, prefix="/clientes", tags=["Clientes"])
app.include_router(productos_api.router, prefix="/productos", tags=["Productos"])
app.include_router(ventas_api.router, prefix="/ventas", tags=["Ventas"])

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# Endpoint raíz
@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API de la Tienda de Ropa"}