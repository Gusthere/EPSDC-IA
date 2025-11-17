from jose import jwt
import time

print(jwt.encode({"username": "test", "exp": int(time.time()) + 3600}, "clave_secreta_compartida", algorithm="HS256"))