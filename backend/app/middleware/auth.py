from fastapi import Request
from fastapi.responses import JSONResponse
import jwt

from app.config import settings

RUTAS_PUBLICAS = {"/api/auth/login"}


async def auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    path = request.url.path
    if not path.startswith("/api/") or path in RUTAS_PUBLICAS:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Token requerido"})

    token = auth_header.removeprefix("Bearer ").strip()
    try:
        jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})

    return await call_next(request)
