import bcrypt

def hash_password(password: str) -> str:
    """
    Genera un hash seguro para la contraseña usando bcrypt.
    Retorna la contraseña encriptada lista para guardar en la base de datos.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si la contraseña ingresada coincide con el hash almacenado.
    Retorna True si es válida, False en caso contrario.
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False