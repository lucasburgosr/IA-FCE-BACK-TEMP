from fastapi import Header, HTTPException, status
from typing import Optional
import jwt, os

JWT_SECRET = os.getenv("JWT_SECRET_KEY")

# Método que valida si el usaurio está autenticado para hacer requests a los distintos endpoints
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el header de autorización",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autenticación inválido",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato del header de autorización inválido",
        )

    try:
        
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=['HS256']
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token expiró"
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No se pudieron validar las credenciales: {e}"
        )