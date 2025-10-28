from fastapi import APIRouter, HTTPException, status
from .db_services import (
    db_obtener_clientes, db_crear_cliente, db_obtener_cliente_por_id,
    db_actualizar_cliente, db_eliminar_cliente
)
from .schemas import ClienteCreate

router = APIRouter()

@router.get("/")
async def listar_clientes():
    return db_obtener_clientes()

@router.get("/{cliente_id}")
async def obtener_cliente(cliente_id: int):
    cliente = db_obtener_cliente_por_id(cliente_id)
    if cliente:
        return cliente
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def agregar_cliente(cliente: ClienteCreate):
    if db_crear_cliente(cliente.nombre, cliente.correo, cliente.telefono, cliente.direccion):
        return {"mensaje": "Cliente agregado correctamente"}
    raise HTTPException(status_code=400, detail="No se pudo agregar el cliente")

@router.put("/{cliente_id}")
async def actualizar_cliente(cliente_id: int, cliente: ClienteCreate):
    if db_actualizar_cliente(cliente_id, cliente.nombre, cliente.correo, cliente.telefono, cliente.direccion):
        return {"mensaje": "Cliente actualizado correctamente"}
    raise HTTPException(status_code=400, detail="No se pudo actualizar el cliente")

@router.delete("/{cliente_id}")
async def eliminar_cliente(cliente_id: int):
    if db_eliminar_cliente(cliente_id):
        return {"mensaje": "Cliente eliminado correctamente"}
    raise HTTPException(status_code=400, detail="No se pudo eliminar el cliente")