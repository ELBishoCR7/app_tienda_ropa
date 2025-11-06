import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# --- LEE LA URL DIRECTAMENTE DEL .ENV ---
DATABASE_URL = os.getenv("DATABASE_URL")
# ----------------------------------------

# Si la URL no se encuentra, lanza un error para evitar problemas
if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL. Asegúrate de que el archivo .env existe y tiene el formato correcto.")

# 'create_engine' es el punto de entrada a la base de datos
engine = create_engine(DATABASE_URL)

# 'SessionLocal' es la clase que usaremos para crear "sesiones" (conexiones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 'Base' es una clase base de la cual heredarán todos nuestros modelos (tablas)
Base = declarative_base()
