# V1.0

# auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from datetime import datetime

# Leer configuración desde config.py (variables de entorno)
from config import SECRET_KEY, JWT_ALGORITHM

security = HTTPBearer()

def verificar_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expirado")
        return payload  # puedes devolver el id_usuario, rol, etc.
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o no autorizado")
