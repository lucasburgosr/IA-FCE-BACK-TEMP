import os
import httpx
import asyncio
import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from firebase_admin import auth
from datetime import datetime, timezone, timedelta
from repositories.usuario_repository import UsuarioRepository
from repositories.estudiante_repository import AlumnoRepository
from schemas.login_schema import LoginInput
from typing import Optional

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Se instancian los repositorios con la sesión asíncrona
        self.usuario_repo = UsuarioRepository(db)
        self.alumno_repo = AlumnoRepository(db)

    async def registrar_alumnos(self, register_data: dict) -> dict:
        # --- Verificación con SIU-Guaraní (ya era asíncrona) ---
        endpoint_verificacion = "http://dashboard.fce.uncu.edu.ar:5000/alutivos/alumnologapp"
        payload = {"documento": register_data.get("nro_documento")}

        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint_verificacion, json=payload, headers={"Content-Type": "application/json"})

        if response.status_code != 201:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes ser estudiante/a o docente de la FCE para acceder al tutor")

        data = response.json()
        if not data or not isinstance(data, list):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Respuesta de verificación inválida")

        alumno_info = data[0]
        if alumno_info.get("claustro") != "EST" or alumno_info.get("calidad") != "A":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No estás habilitado/a para registrarte en el Tutor")

        # --- Creación de usuario en Firebase ---
        try:
            firebase_user = await asyncio.to_thread(auth.create_user, email=register_data.get("email"), password=register_data.get("password"))
            firebase_uid = firebase_user.uid
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear usuario en Firebase: {str(e)}")

        # --- Verificación y creación en la base de datos ---
        try:
            # 1. Se espera la consulta al repositorio de usuarios
            existing_user = await self.usuario_repo.get_by_email(alumno_info.get("email"))
            if existing_user:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya estás registrado en el Tutor. Inicia sesión.")

            estudiante_data = {
                "nombres": register_data.get("nombres"),
                "apellido": register_data.get("apellido"),
                "email": register_data.get("email"),
                "nro_documento": register_data.get("nro_documento"),
            }
            # 2. Se espera la creación en el repositorio de alumnos.
            #    El método 'create' del repo ya se encarga del commit.
            await self.alumno_repo.create(estudiante_data)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al registrar el usuario en la base de datos: {str(e)}")

        return {
            "message": "Usuario registrado exitosamente",
            "email": register_data.get("email") # Se usa el email del registro, no el de la variable 'estudiante' que era un dict
        }
    
    async def registrar_alumnos_econet(self, register_data: dict) -> dict:
        # --- Verificación con SIU-Guaraní ---
        endpoint_verificacion = "http://dashboard.fce.uncu.edu.ar:5000/alutivos/alumnologapp"
        payload = {"documento": register_data.get("nro_documento")}

        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint_verificacion, json=payload, headers={"Content-Type": "application/json"})

        if response.status_code != 201:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes ser estudiante/a o docente de la FCE para acceder al tutor")

        data = response.json()
        if not data or not isinstance(data, list):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Respuesta de verificación inválida")

        alumno_info = data[0]
        if alumno_info.get("claustro") != "EST" or alumno_info.get("calidad") != "A":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No estás habilitado/a para registrarte en el Tutor")

        # --- Verificación y creación en la base de datos ---
        try:
            estudiante_data = {
                "nombres": register_data.get("nombres"),
                "apellido": register_data.get("apellido"),
                "email": register_data.get("email"),
                "nro_documento": register_data.get("nro_documento"),
            }
            await self.alumno_repo.create(estudiante_data)

        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al registrar el usuario en la base de datos: {str(e)}")

        return {
            "message": "Usuario registrado exitosamente",
            "email": register_data.get("email")
        }

    async def iniciar_sesion(self, login_data: LoginInput) -> dict:

        usuario = await self.usuario_repo.get_by_email(email=login_data.email)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No estás registrado como usuario. Regístrate para poder iniciar sesión.")

        # Lógica de actualización mejorada
        if usuario.type == "estudiante":
            estudiante = await self.alumno_repo.get_by_id(id=usuario.id)
            if estudiante:
                await self.alumno_repo.update(estudiante, {"last_login": datetime.now(tz=None)})

        payload = {
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        
        token = jwt.encode(payload=payload,key=JWT_SECRET,algorithm="HS256")

        return {
            "token": token,
            "usuario_id": usuario.id,
            "email_usuario": usuario.email,
            "type": usuario.type
        }
        
    async def iniciar_sesion_econet(self, email: str, curso: Optional[str] = None) -> dict:

        if isinstance(curso, str):
            print("Entra 1")
            usuario = await self.usuario_repo.get_by_email_docente_estudiante(email=email)
        else:
            print("Entra 2")
            usuario = await self.usuario_repo.get_by_email(email=email)

        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No estás registrado como usuario. Regístrate para poder iniciar sesión.")
        else:
            print("usuario:", getattr(usuario, "email", None), getattr(usuario, "type", None))

        # Lógica de actualización mejorada
        if usuario.type == "estudiante":
            estudiante = await self.alumno_repo.get_by_id(id=usuario.id)
            if estudiante:
                await self.alumno_repo.update(estudiante, {"last_login": datetime.now(tz=None)})

        # 2. Actualizar usuario de forma asíncrona
        # await self.usuario_repo.update(usuario=usuario, update_data={"firebase_uid": firebase_uid})
        
        payload = {
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        
        token = jwt.encode(payload=payload,key=JWT_SECRET,algorithm="HS256")
        
        return {
            "token": token,
            "usuario_id": usuario.id,
            "email_usuario": usuario.email,
            "type": usuario.type
        }