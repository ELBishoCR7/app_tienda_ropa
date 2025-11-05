from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- ¡IMPORTANTE! ACTUALIZA ESTA LÍNEA ---
# Formato: "mysql+mysqlconnector://[USUARIO]:[PASSWORD]@[HOST]:[PUERTO]/[NOMBRE_DB]"
DATABASE_URL = "mysql+mysqlconnector://root:Saul25591@127.0.0.1:3306/tienda_db"
# ----------------------------------------

# 'create_engine' es el punto de entrada a la base de datos
engine = create_engine(DATABASE_URL)

# 'SessionLocal' es la clase que usaremos para crear "sesiones" (conexiones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 'Base' es una clase base de la cual heredarán todos nuestros modelos (tablas)
Base = declarative_base()