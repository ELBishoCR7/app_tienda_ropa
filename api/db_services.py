from db import gestor_db
from datetime import datetime

#  Crear cliente
def db_crear_cliente(nombre: str, correo: str, telefono: str, direccion: str) -> bool:
    query = """
        INSERT INTO clientes (nombre, correo, telefono, direccion)
        VALUES (%s, %s, %s, %s)
    """
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (nombre, correo, telefono, direccion))
                conn.commit()
                return True
        return False
    except Exception as e:
        print(f"Error in db_crear_cliente: {e}")
        return False


#  Obtener todos los clientes
def db_obtener_clientes():
    query = "SELECT id, nombre, correo, telefono, direccion FROM clientes"
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query)
                return cursor.fetchall()
        return []
    except Exception as e:
        print(f"Error in db_obtener_clientes: {e}")
        return []


#  Buscar cliente por ID
def db_obtener_cliente_por_id(cliente_id: int):
    query = "SELECT id, nombre, correo, telefono, direccion FROM clientes WHERE id=%s"
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (cliente_id,))
                return cursor.fetchone()
        return None
    except Exception as e:
        print(f"Error in db_obtener_cliente_por_id: {e}")
        return None


#  Actualizar cliente
def db_actualizar_cliente(cliente_id: int, nombre: str, correo: str, telefono: str, direccion: str) -> bool:
    query = """
        UPDATE clientes
        SET nombre=%s, correo=%s, telefono=%s, direccion=%s
        WHERE id=%s
    """
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (nombre, correo, telefono, direccion, cliente_id))
                conn.commit()
                return True
        return False
    except Exception as e:
        print(f"Error in db_actualizar_cliente: {e}")
        return False



#  Eliminar cliente
def db_eliminar_cliente(cliente_id: int) -> bool:
    query = "DELETE FROM clientes WHERE id=%s"
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (cliente_id,))
                conn.commit()
                return True
        return False
    except Exception as e:
        print(f"Error in db_eliminar_cliente: {e}")
        return False

#  Crear producto
def db_crear_producto(nombre: str, descripcion: str, precio: float, stock: int, talla: str, categoria: str) -> bool:
    query = """
        INSERT INTO productos (nombre, descripcion, precio, stock, talla, categoria)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (nombre, descripcion, precio, stock, talla, categoria))
                conn.commit()
                return True
        return False
    except Exception as e:
        print(f"Error in db_crear_producto: {e}")
        return False


#  Obtener todos los productos
def db_obtener_productos():
    query = "SELECT id, nombre, descripcion, precio, stock, talla, categoria FROM productos"
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query)
                return cursor.fetchall()
        return []
    except Exception as e:
        print(f"Error in db_obtener_productos: {e}")
        return []


#  Buscar producto por ID
def db_obtener_producto_por_id(producto_id: int):
    query = """
        SELECT id, nombre, descripcion, precio, stock, talla, categoria
        FROM productos WHERE id=%s
    """
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (producto_id,))
                return cursor.fetchone()
        return None
    except Exception as e:
        print(f"Error in db_obtener_producto_por_id: {e}")
        return None


#  Actualizar producto
def db_actualizar_producto(producto_id: int, nombre: str, descripcion: str, precio: float, stock: int, talla: str, categoria: str) -> bool:
    query = """
        UPDATE productos
        SET nombre=%s, descripcion=%s, precio=%s, stock=%s, talla=%s, categoria=%s
        WHERE id=%s
    """
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (nombre, descripcion, precio, stock, talla, categoria, producto_id))
                conn.commit()
                return True
        return False
    except Exception as e:
        print(f"Error in db_actualizar_producto: {e}")
        return False


#  Eliminar producto
def db_eliminar_producto(producto_id: int) -> bool:
    query = "DELETE FROM productos WHERE id=%s"
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (producto_id,))
                conn.commit()
                return True
        return False
    except Exception as e:
        print(f"Error in db_eliminar_producto: {e}")
        return False

# 📝 Registrar una venta
def db_registrar_venta(cliente_id: int, productos: list, total: float) -> bool:
    try:
        with gestor_db() as (conn, cursor):
            if not conn:
                return False

            # Insertar en tabla ventas
            fecha = datetime.now()
            cursor.execute(
                "INSERT INTO ventas (fecha, cliente_id, total) VALUES (%s, %s, %s)",
                (fecha, cliente_id, total)
            )
            venta_id = cursor.lastrowid

            # Preparar datos para detalles_venta y actualización de stock
            detalles_data = []
            for producto_id, cantidad, precio_unitario in productos:
                detalles_data.append((venta_id, producto_id, cantidad, precio_unitario))

            # Insertar en detalles_venta (usando executemany para eficiencia)
            cursor.executemany(
                "INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                detalles_data
            )

            # Actualizar stock del producto
            for producto_id, cantidad, _ in productos:
                cursor.execute("UPDATE productos SET stock = stock - %s WHERE id = %s", (cantidad, producto_id))

            conn.commit()
            return True
    except Exception as e:
        print(f"Error in db_registrar_venta: {e}")
        return False


# 📋 Obtener todas las ventas
def db_obtener_ventas():
    query = """
        SELECT v.id, v.fecha, c.nombre, v.total
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.fecha DESC
    """
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query)
                return cursor.fetchall()
        return []
    except Exception as e:
        print(f"Error in db_obtener_ventas: {e}")
        return []


# 🔍 Obtener detalles de una venta
def db_obtener_detalles_venta(venta_id: int):
    query = """
        SELECT p.nombre, dv.cantidad, dv.precio_unitario, (dv.cantidad * dv.precio_unitario) as subtotal
        FROM detalles_venta dv
        JOIN productos p ON dv.producto_id = p.id
        WHERE dv.venta_id = %s
    """
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (venta_id,))
                return cursor.fetchall()
        return []
    except Exception as e:
        print(f"Error in db_obtener_detalles_venta: {e}")
        return []
