# V1.0

# auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from datetime import datetime

# Debe ser la MISMA clave secreta usada por el backend PHP
SECRET_KEY = "tu_clave_jwt_compartida"
ALGORITHM = "HS256"

security = HTTPBearer()

def verificar_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expirado")
        return payload  # puedes devolver el id_usuario, rol, etc.
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o no autorizado")
