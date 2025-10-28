from pydantic import BaseModel, Field, EmailStr
from typing import List

# --- Esquemas de Cliente ---
class ClienteBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str
    direccion: str

class ClienteCreate(ClienteBase):
    pass

# --- Esquemas de Producto ---
class ProductoBase(BaseModel):
    nombre: str
    descripcion: str
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    talla: str
    categoria: str

class ProductoCreate(ProductoBase):
    pass

# --- Esquemas de Venta ---
class VentaCreate(BaseModel):
    cliente_id: int
    productos: List[dict] # Lista de {"producto_id": int, "cantidad": int, "precio_unitario": float}
    total: float