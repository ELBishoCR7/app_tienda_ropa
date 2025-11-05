from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, security, status
from fastapi.security import OAuth2PasswordBearer

# --- Configuración de Hashing (ya lo teníamos) ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- ¡NUEVO! Configuración de JWT ---
# IMPORTANTE: ¡Genera tu propia llave secreta!
# Puedes usar un generador de contraseñas online para esto.
# Debe ser una cadena larga y aleatoria.
SECRET_KEY = "gnq<`7*M9{4oZ&2H!v$uL?8zWqXc>e@Yp3JrF)h%N1bO6S+gV0yI|jE#R]t;A" 
ALGORITHM = "HS256"
URLKEY = "mysql+mysqlconnector://root:Saul25591@127.0.0.1:3306/tienda_db"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # El token será válido por 30 minutos

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash para una contraseña plana."""
    return pwd_context.hash(password)

# --- ¡NUEVO! Funciones para crear y validar Tokens ---

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crea un nuevo token de acceso (JWT)."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Por defecto, expira en 15 minutos si no se especifica
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    
    # "Firma" el token con nuestra llave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_token_payload(token: str) -> dict:
    """
    Decodifica y valida un token JWT.
    Devuelve el "payload" (los datos) si es válido.
    """
    try:
        # Intenta decodificar el token usando nuestra llave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extraemos el email (que guardamos como 'sub')
        user_email: str | None = payload.get("sub")
        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido (no contiene 'sub')",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
        
    except JWTError:
        # El token expiró o la firma no coincide
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )