from dotenv import load_dotenv
import os
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URL de la base de datos desde la variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")


def create_engine_with_retry(database_url, max_retries=5, initial_delay=2):
    """
    Crea un engine de SQLAlchemy con reintentos exponenciales.

    Args:
        database_url: URL de conexión a la base de datos
        max_retries: Número máximo de intentos (default: 5)
        initial_delay: Delay inicial en segundos (default: 2)

    Returns:
        Engine de SQLAlchemy configurado

    Raises:
        OperationalError: Si falla después de todos los reintentos
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            logger.info(f"Intento {attempt + 1}/{max_retries}: Creando engine de base de datos...")

            # Crear engine con configuración resiliente
            engine = create_engine(
                database_url,
                pool_pre_ping=True,  # Verifica conexiones antes de usarlas
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,  # Recicla conexiones cada hora
                connect_args={
                    "connect_timeout": 10,
                }
            )

            # Probar la conexión
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("Conexión a la base de datos exitosa!")
            return engine

        except OperationalError as e:
            last_exception = e

            if "not yet accepting connections" in str(e) or "Consistent recovery state" in str(e):
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    logger.warning(
                        f"Base de datos en recuperación. "
                        f"Reintentando en {delay} segundos... "
                        f"(intento {attempt + 1}/{max_retries})"
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"Base de datos no disponible después de {max_retries} intentos")
                    raise
            else:
                # Si es otro tipo de error, lanzarlo inmediatamente
                logger.error(f"Error de conexión a la base de datos: {e}")
                raise

    # Si llegamos aquí, es porque se agotaron los reintentos
    raise last_exception


# Crear engine con reintentos
engine = create_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


