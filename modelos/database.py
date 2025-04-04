from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://ibm_cloud_9b28f112_cd7b_4807_b8c2_b3a0ff511e01:MILnbZ0yQkISTKuWZbeQxZTrCr8a0DKr@4d437ecc-844f-4a46-b103-32f5ebefe84a.0135ec03d5bf43b196433793c98e8bd5.databases.appdomain.cloud:30429/ibmclouddb"

engine = create_engine(DATABASE_URL )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

