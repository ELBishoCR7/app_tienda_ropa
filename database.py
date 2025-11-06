from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()



# 'create_engine' es el punto de entrada a la base de datos
engine = create_engine(os.getenv("DATABASE_URL"))

# 'SessionLocal' es la clase que usaremos para crear "sesiones" (conexiones)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 'Base' es una clase base de la cual heredarán todos nuestros modelos (tablas)
Base = declarative_base()