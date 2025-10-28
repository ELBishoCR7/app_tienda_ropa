import mysql.connector
from contextlib import contextmanager
from config import DB_CONFIG

def conectar():
    """Establece conexión con la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

def verificar_conexion():
    """Verifica la conexión con la base de datos y la cierra."""
    conn = conectar()
    if conn:
        print("Conexión a la base de datos exitosa.")
        conn.close()
        return True
    return False

@contextmanager
def gestor_db():
    """
    Un gestor de contexto para manejar las conexiones y cursores de la BD.
    Asegura que la conexión se cierre correctamente.
    """
    conn = conectar()
    if conn is None:
        yield None, None
        return
    
    cursor = conn.cursor()
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()