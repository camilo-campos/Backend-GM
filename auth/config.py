import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de IBM App ID
IBM_APPID_TENANT_ID = os.getenv("IBM_APPID_TENANT_ID", "85e29de8-031c-4ea9-baf3-4d196998a2bb")
IBM_APPID_REGION = os.getenv("IBM_APPID_REGION", "us-south")
IBM_APPID_CLIENT_ID = os.getenv("IBM_APPID_CLIENT_ID", "25e71bc4-15ee-4837-946a-ecf8015c775c")

# URLs derivadas
IBM_APPID_BASE_URL = f"https://{IBM_APPID_REGION}.appid.cloud.ibm.com/oauth/v4/{IBM_APPID_TENANT_ID}"
IBM_APPID_JWKS_URL = f"{IBM_APPID_BASE_URL}/publickeys"
IBM_APPID_ISSUER = IBM_APPID_BASE_URL

# Configuración de validación
JWT_ALGORITHM = "RS256"
JWT_AUDIENCE = IBM_APPID_CLIENT_ID

# Configuración de caché para JWKS (en segundos)
JWKS_CACHE_TTL = 3600  # 1 hora
