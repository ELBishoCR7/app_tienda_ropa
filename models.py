from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, DateTime
from database import Base # Importamos la 'Base' que creamos
from sqlalchemy.orm import relationship # ¡Añade esta importación!
from datetime import datetime # ¡Añade esta importación!


class User(Base):
    """Modelo de la tabla 'users'."""
    
    __tablename__ = "users" # Nombre de la tabla en MySQL

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(100)) # String(100) es como VARCHAR(100)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False) # Guardamos el hash, no la pass
    is_admin = Column(Boolean, default=False)
    # --- NUEVOS CAMPOS DE DIRECCIÓN ---
    direccion = Column(Text, nullable=True)       # calle / avenida, etc.
    ciudad = Column(String(100), nullable=True)
    estado = Column(String(100), nullable=True)
    codigo_postal = Column(String(20), nullable=True)
    pais = Column(String(100), nullable=True)
    telefono = Column(String(50), nullable=True)
    # ---------------------------------------------
    ventas = relationship("Venta", back_populates="cliente")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")  # <-- NEW
    
    # Aquí podríamos añadir más campos: direccion, telefono, etc.
class Product(Base):
    """Modelo de la tabla 'products'."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    # Guardamos la URL de la imagen, no la imagen en sí
    imagen_url = Column(String(255), nullable=True)

    # ... (Después de la clase Product) ...

class Venta(Base):
    """Modelo de la tabla 'ventas' (Pedidos)."""
    
    __tablename__ = "ventas"
    
    id = Column(Integer, primary_key=True, index=True)
    # default=datetime.now(timezone.utc) si usas UTC, o solo datetime.now
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    
    # --- Llave Foránea ---
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # --- Relaciones (Links de SQLAlchemy) ---
    
    # Vínculo con User: Una Venta pertenece a un User
    # 'back_populates' conecta esta relación con la de User.
    cliente = relationship("User", back_populates="ventas")
    
    # Vínculo con VentaItem: Una Venta tiene muchos VentaItems
    items = relationship("VentaItem", back_populates="venta", cascade="all, delete-orphan")

class VentaItem(Base):
    """Modelo de la tabla 'venta_items' (Líneas de pedido)."""
    
    __tablename__ = "venta_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Integer, nullable=False)
    # Guardamos el precio al momento de la venta
    precio_unitario = Column(Float, nullable=False) 
    
    # --- Llaves Foráneas ---
    venta_id = Column(Integer, ForeignKey("ventas.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # --- Relaciones ---
    
    # Vínculo con Venta: Un Item pertenece a una Venta
    venta = relationship("Venta", back_populates="items")
    
    # Vínculo con Product: Un Item se refiere a un Producto
    # (No necesitamos back_populates en Product, 
    # a menos que queramos ver las ventas desde el producto)
    producto = relationship("Product")

# NEW: Modelo para elementos del carrito (cart_items)
class CartItem(Base):
    """Modelo de la tabla 'cart_items' (elementos temporales del carrito por usuario)."""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False)  # precio tomado al agregar

    user = relationship("User", back_populates="cart_items")
    producto = relationship("Product")