from db import gestor_db
from login.utils import hash_password, verify_password

#  Autenticación de usuario
def autenticar_usuario(correo: str, contraseña: str):
    """
    Verifica si el usuario existe y la contraseña es correcta.
    Devuelve una tupla (rol, id) si es válido, None si no.
    """
    query = "SELECT id, password, rol FROM usuarios WHERE correo=%s"
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (correo,))
                resultado = cursor.fetchone()
                if resultado:
                    user_id, contraseña_hash, rol = resultado
                    if verify_password(contraseña, contraseña_hash):
                        return rol, user_id
        return None
    except Exception as e:
        print(f"Error en autenticar_usuario: {e}")
        return None


#  Registro de usuario
def registrar_usuario(nombre: str, correo: str, contraseña: str, rol: str = "cliente"):
    """
    Registra un nuevo usuario en la base de datos.
    Por defecto, el tipo es 'cliente'. El admin se crea manualmente o con un script.
    """
    query = """
        INSERT INTO usuarios (nombre, correo, password, rol)
        VALUES (%s, %s, %s, %s)
    """
    try:
        contraseña_hash = hash_password(contraseña)
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (nombre, correo, contraseña_hash, rol))
                conn.commit()
                return True
        return False
    except Exception as e:
        print(f"Error en registrar_usuario: {e}")
        return False


#  Verificar si un correo ya existe
def usuario_existe(correo: str) -> bool:
    """
    Verifica si ya existe un usuario con ese correo.
    """
    query = "SELECT id FROM usuarios WHERE correo=%s"
    try:
        with gestor_db() as (conn, cursor):
            if conn:
                cursor.execute(query, (correo,))
                return cursor.fetchone() is not None
        return False
    except Exception as e:
        print(f"Error en usuario_existe: {e}")
        return False