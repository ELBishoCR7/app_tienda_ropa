from fastapi import APIRouter, HTTPException, status
from .db_services import (
    db_obtener_productos, db_crear_producto, db_obtener_producto_por_id,
    db_actualizar_producto, db_eliminar_producto
)
from .schemas import ProductoCreate

router = APIRouter()

@router.get("/")
async def listar_productos():
    return db_obtener_productos()

@router.get("/{producto_id}")
async def obtener_producto(producto_id: int):
    producto = db_obtener_producto_por_id(producto_id)
    if producto:
        return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def agregar_producto(producto: ProductoCreate):
    if db_crear_producto(producto.nombre, producto.descripcion, producto.precio, producto.stock, producto.talla, producto.categoria):
        return {"mensaje": "Producto agregado correctamente"}
    raise HTTPException(status_code=400, detail="No se pudo agregar el producto")

@router.put("/{producto_id}")
async def actualizar_producto(producto_id: int, producto: ProductoCreate):
    if db_actualizar_producto(producto_id, producto.nombre, producto.descripcion, producto.precio, producto.stock, producto.talla, producto.categoria):
        return {"mensaje": "Producto actualizado correctamente"}
    raise HTTPException(status_code=400, detail="No se pudo actualizar el producto")

@router.delete("/{producto_id}")
async def eliminar_producto(producto_id: int):
    if db_eliminar_producto(producto_id):
        return {"mensaje": "Producto eliminado correctamente"}
    raise HTTPException(status_code=400, detail="No se pudo eliminar el producto")