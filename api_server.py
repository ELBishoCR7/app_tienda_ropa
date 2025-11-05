from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session # Para interactuar con la DB
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import models
import security   
from database import SessionLocal, engine # Importa la config de DB
from typing import List
from security import oauth2_scheme, verify_token_payload
from sqlalchemy.orm import joinedload # ¡NUEVO! Para optimizar la consulta
from datetime import datetime

# --- 1. Creación de las Tablas ---
# Esta línea le dice a SQLAlchemy que cree todas las tablas
# definidas en models.py (en este caso, la tabla 'users')
# si es que no existen ya.
models.Base.metadata.create_all(bind=engine)


# --- 2. Modelos Pydantic (Validación de entrada) ---
class UserRegister(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    direccion: str | None = None
    ciudad: str | None = None
    estado: str | None = None
    codigo_postal: str | None = None
    pais: str | None = None
    telefono: str | None = None

    @validator("nombre_completo")
    def nombre_min_length(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v.strip()

    @validator("codigo_postal")
    def validar_codigo_postal(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r"^[A-Za-z0-9\s\-]{3,10}$", v):
            raise ValueError("Código postal inválido")
        return v.strip()

    @validator("telefono")
    def validar_telefono(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r"^\+?[0-9\s\-]{7,20}$", v):
            raise ValueError("Teléfono inválido")
        return v.strip()

    @validator("direccion", "ciudad", "estado", "pais")
    def strip_strings(cls, v):
        if v is None:
            return v
        return v.strip()

class Token(BaseModel):
    """Modelo Pydantic para la respuesta del token."""
    access_token: str
    token_type: str
    is_admin: bool = False # ¡NUEVO CAMPO!

    # ... (clase Token) ...

class ProductSchema(BaseModel):
    """
    Schema Pydantic para DEVOLVER un producto.
    No incluye campos sensibles.
    """
    id: int
    nombre: str
    descripcion: str | None = None
    precio: float
    stock: int
    imagen_url: str | None = None
    
    # Esto le dice a Pydantic que puede leer
    # el modelo desde un objeto SQLAlchemy (modo ORM)
    class Config:
        from_attributes = True

# ... (clase UserRegister) ...

# ... (clase ProductSchema) ...

class VentaItemSchema(BaseModel):
    """Schema Pydantic para un item dentro de una venta."""
    id: int
    cantidad: int
    precio_unitario: float
    product_id: int # Para saber qué producto fue
    
    class Config:
        from_attributes = True


class VentaSchema(BaseModel):
    """Schema Pydantic para una Venta completa."""
    id: int
    fecha: datetime
    total: float
    user_id: int # Para saber qué cliente compró
    
    # ¡Aquí anidamos la lista de items!
    items: List[VentaItemSchema] = []
    
    class Config:
        from_attributes = True

class ProfileSchema(BaseModel):
    """Schema Pydantic para DEVOLVER el perfil del usuario."""
    id: int
    nombre_completo: str
    email: EmailStr
    is_admin: bool
    # NUEVOS CAMPOS DE DIRECCIÓN
    direccion: str | None = None
    ciudad: str | None = None
    estado: str | None = None
    codigo_postal: str | None = None
    pais: str | None = None
    telefono: str | None = None

    class Config:
        from_attributes = True

class ProfileUpdateSchema(BaseModel):
    """
    Schema Pydantic para RECIBIR actualizaciones del perfil.
    Hacemos los campos opcionales por si solo quiere cambiar uno.
    """
    nombre_completo: str | None = None
    email: EmailStr | None = None
    # Campos de dirección opcionales
    direccion: str | None = None
    ciudad: str | None = None
    estado: str | None = None
    codigo_postal: str | None = None
    pais: str | None = None
    telefono: str | None = None

    @validator("nombre_completo")
    def nombre_min_length(cls, v):
        if v is None:
            return v
        if len(v.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v.strip()

    @validator("codigo_postal")
    def validar_codigo_postal(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r"^[A-Za-z0-9\s\-]{3,10}$", v):
            raise ValueError("Código postal inválido")
        return v.strip()

    @validator("telefono")
    def validar_telefono(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r"^\+?[0-9\s\-]{7,20}$", v):
            raise ValueError("Teléfono inválido")
        return v.strip()

    @validator("pais", "ciudad", "estado", "direccion")
    def strip_strings(cls, v):
        if v is None:
            return v
        return v.strip()

class ProductCreate(BaseModel):
    """Schema para crear/actualizar productos."""
    nombre: str
    descripcion: str | None = None
    precio: float
    stock: int
    imagen_url: str | None = None

class CartItemCreate(BaseModel):
    product_id: int
    cantidad: int

class CartItemSchema(BaseModel):
    id: int
    product_id: int
    cantidad: int
    precio_unitario: float
    # Agregamos datos del producto para facilitar el front (opcional)
    nombre: str | None = None
    imagen_url: str | None = None
    stock: int | None = None  # <-- NEW: stock disponible

    class Config:
        from_attributes = True

class CartSchema(BaseModel):
    items: List[CartItemSchema] = []
    total: float = 0.0

    class Config:
        from_attributes = True




# --- 3. Instancia de la App ---
app = FastAPI(
    title="API de Tienda E-Commerce",
    description="La API REST para la aplicación de tienda de ropa.",
    version="0.1.0"
)

# --- 4. Dependencia de Base de Datos ---
# Esto es "Inyección de Dependencias".
# FastAPI creará una nueva sesión (SessionLocal) por cada request
# y la cerrará al terminar.
def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependencia que valida el token y devuelve el
    objeto de usuario de la base de datos.
    """
    payload = verify_token_payload(token)
    email: str = payload.get("sub")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado"
        )
    return user

def get_current_admin_user(
        

    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Dependencia que verifica que el usuario actual
    sea un administrador.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador."
        )
    return current_user
# --- 5. Endpoints de la API ---

@app.get("/")
async def root():
    return {"message": "¡Bienvenido a la API de la Tienda!"}


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    """
    Endpoint para registrar un nuevo usuario.
    Ahora guarda en la base de datos MySQL.
    """
    
    # A. Verificar si el email ya existe
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )
    
    # B. Hashear la contraseña
    hashed_password = security.get_password_hash(user.password)
    
    # C. Crear el nuevo objeto de usuario para la DB (incluye datos de dirección)
    new_db_user = models.User(
        email=user.email,
        nombre_completo=user.nombre_completo,
        hashed_password=hashed_password,
        direccion=user.direccion,
        ciudad=user.ciudad,
        estado=user.estado,
        codigo_postal=user.codigo_postal,
        pais=user.pais,
        telefono=user.telefono
        # is_admin se queda como False (valor por defecto)
    )
    
    # D. Guardar en la base de datos
    db.add(new_db_user)  # Añade el objeto a la sesión
    db.commit()         # Confirma la transacción (guarda en la DB)
    db.refresh(new_db_user) # Refresca el objeto (para obtener el ID creado)

    return {
        "message": "Usuario creado exitosamente",
        "user_id": new_db_user.id,
        "email": new_db_user.email
    }

# ... (tu endpoint /api/register) ...


@app.post("/api/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión y obtener un token JWT.
    """
    
    # 1. Buscar al usuario por email
    # Usamos form_data.username porque OAuth2 usa "username" en lugar de "email"
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Verificar si el usuario existe Y si la contraseña es correcta
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Crear el token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Guardamos el ID de usuario y si es admin en el token
    # Esto es el "payload" o los "datos" del token
    data_para_token = {
        "sub": user.email,  # 'sub' (subject) es el estándar para identificar al usuario
        "id": user.id,
        "is_admin": user.is_admin 
    }
    
    access_token = security.create_access_token(
        data=data_para_token, expires_delta=access_token_expires
    )
    
    # 4. Devolver el token Y el rol
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "is_admin": user.is_admin # ¡NUEVA LÍNEA!
    }

# ... (tu endpoint /api/login) ...

@app.get("/api/products", response_model=List[ProductSchema])
async def get_all_products(

    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # ¡Protegido!
):
    """
    Obtiene todos los productos de la tienda.
    Esta ruta está protegida: solo usuarios logueados pueden verla.
    """
    print(f"El usuario {current_user.email} está pidiendo los productos.")
    
    products = db.query(models.Product).all()
    return products

@app.get("/api/admin/sales", response_model=List[VentaSchema])
async def get_all_sales(

    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user) # ¡Protegido!
):
    """
    Obtiene TODAS las ventas de la base de datos.
    Ruta protegida: solo para administradores.
    """
    print(f"El admin {admin_user.email} está pidiendo todas las ventas.")
    
    # Consultamos las ventas.
    # Usamos 'joinedload' para "traer" los items de cada venta
    # en la misma consulta (Eager Loading). Esto es mucho más eficiente
    # que hacer una consulta separada por cada venta (N+1 problem).
    ventas = db.query(models.Venta).options(
        joinedload(models.Venta.items)
    ).order_by(models.Venta.fecha.desc()).all()
    
    return ventas

@app.get("/api/profile", response_model=ProfileSchema)
async def get_user_profile(
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtiene el perfil del usuario actualmente logueado.
    """
    # La dependencia 'get_current_user' ya hizo todo el trabajo
    # de buscar al usuario en la DB a partir del token.
    return current_user


@app.put("/api/profile", response_model=ProfileSchema)
async def update_user_profile(
    update_data: ProfileUpdateSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Actualiza el perfil (nombre, email y datos de dirección) del usuario logueado.
    """
    user_updated = False # Para saber si necesitamos hacer commit

    # 1. Actualizar Nombre (si se proporcionó)
    if update_data.nombre_completo is not None and update_data.nombre_completo != current_user.nombre_completo:
        current_user.nombre_completo = update_data.nombre_completo
        user_updated = True

    # 2. Actualizar Email (si se proporcionó)
    if update_data.email is not None and update_data.email != current_user.email:
        # ¡IMPORTANTE! Verificar que el nuevo email no esté ya en uso
        existing_user = db.query(models.User).filter(models.User.email == update_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo email ya está registrado por otro usuario."
            )
        current_user.email = update_data.email
        user_updated = True

    # 3. Campos de dirección (si se proporcionaron)
    addr_fields = ["direccion", "ciudad", "estado", "codigo_postal", "pais", "telefono"]
    for field in addr_fields:
        val = getattr(update_data, field)
        if val is not None and getattr(current_user, field) != val:
            setattr(current_user, field, val)
            user_updated = True
    
    # 4. Guardar cambios en la DB (si hubo alguno)
    if user_updated:
        db.commit()
        db.refresh(current_user)
    
    return current_user

@app.post("/api/admin/products", response_model=ProductSchema)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """Crea un nuevo producto (solo admin)."""
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/api/admin/products/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """Actualiza un producto existente (solo admin)."""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/admin/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """Elimina un producto (solo admin)."""
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Producto eliminado"}

@app.get("/api/cart", response_model=CartSchema)
async def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Devuelve el carrito del usuario actual."""
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    items_out = []
    total = 0.0
    for ci in cart_items:
        nombre = ci.producto.nombre if ci.producto else None
        imagen = ci.producto.imagen_url if ci.producto else None
        stock = ci.producto.stock if ci.producto else None  # <-- NEW: incluir stock
        items_out.append({
            "id": ci.id,
            "product_id": ci.product_id,
            "cantidad": ci.cantidad,
            "precio_unitario": ci.precio_unitario,
            "nombre": nombre,
            "imagen_url": imagen,
            "stock": stock
        })
        total += ci.cantidad * ci.precio_unitario
    return {"items": items_out, "total": total}

@app.post("/api/cart/add", response_model=CartSchema)
async def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Añade un producto al carrito (o actualiza la cantidad)."""
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if item.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad debe ser mayor que 0")
    if product.stock < item.cantidad:
        raise HTTPException(status_code=400, detail="No hay stock suficiente")

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == item.product_id
    ).first()
    if cart_item:
        new_cant = cart_item.cantidad + item.cantidad
        if new_cant > product.stock:
            raise HTTPException(status_code=400, detail="Cantidad total excede stock disponible")
        cart_item.cantidad = new_cant
    else:
        cart_item = models.CartItem(
            user_id=current_user.id,
            product_id=item.product_id,
            cantidad=item.cantidad,
            precio_unitario=product.precio
        )
        db.add(cart_item)
    db.commit()

    # Devolver carrito actualizado
    return await get_cart(db, current_user)

@app.put("/api/cart/update/{product_id}", response_model=CartSchema)
async def update_cart_item(
    product_id: int,
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Actualiza cantidad de un item del carrito (reemplaza cantidad)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if item.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad debe ser mayor que 0")
    if product.stock < item.cantidad:
        raise HTTPException(status_code=400, detail="No hay stock suficiente")

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == product_id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item en carrito no existe")
    cart_item.cantidad = item.cantidad
    db.commit()
    return await get_cart(db, current_user)

@app.delete("/api/cart/remove/{product_id}", response_model=CartSchema)
async def remove_cart_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Elimina un item del carrito."""
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == product_id
    ).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
    return await get_cart(db, current_user)

@app.post("/api/cart/checkout", response_model=VentaSchema)
async def checkout_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Finaliza la compra:
    - Valida stock
    - Crea Venta y VentaItems
    - Resta stock de productos
    - Limpia el carrito del usuario
    """
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Carrito vacío")
    total = 0.0
    # Validar stock primero
    for ci in cart_items:
        prod = db.query(models.Product).filter(models.Product.id == ci.product_id).with_for_update().first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto {ci.product_id} no encontrado")
        if prod.stock < ci.cantidad:
            raise HTTPException(status_code=400, detail=f"No hay stock suficiente para {prod.nombre}")

    # Crear venta
    venta = models.Venta(user_id=current_user.id, total=0.0)
    db.add(venta)
    db.flush()  # obtener id de venta

    for ci in cart_items:
        prod = db.query(models.Product).filter(models.Product.id == ci.product_id).first()
        line_total = ci.cantidad * ci.precio_unitario
        total += line_total
        venta_item = models.VentaItem(
            venta_id=venta.id,
            product_id=ci.product_id,
            cantidad=ci.cantidad,
            precio_unitario=ci.precio_unitario
        )
        db.add(venta_item)
        # Descontar stock
        prod.stock = prod.stock - ci.cantidad

    venta.total = total
    db.commit()

    # Limpiar carrito
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()

    # Refrescar venta para devolverla
    db.refresh(venta)
    return venta