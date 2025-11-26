from repositories.usuario_repository import UsuarioRepository
from typing import Dict, Any, List, Optional
from models.usuario import Usuario
from services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse, unquote


class UsuarioService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.usuario_repo = UsuarioRepository(db)
        self.auth_service = AuthService(db)

    async def check_login_or_register(self, login_data) -> Usuario:
        usuario = await self.usuario_repo.get_by_email(email=login_data.get("email"))
        if not usuario:
            print("Entrando a registro de alumno")
            register_data = {
                "nombres": login_data.get("nombres"),
                "apellido": login_data.get("apellido"),
                "email": login_data.get("email"),
                "nro_documento": int(login_data.get("dni")),
                "type": "estudiante"
            }
            await self.auth_service.registrar_alumnos_econet(register_data=register_data)
            usuario_login = await self.auth_service.iniciar_sesion_econet(login_data.get("email"), login_data.get("curso"))
        else:
            print("El alumno ya existía")
            usuario_login = await self.auth_service.iniciar_sesion_econet(login_data.get("email"), login_data.get("curso"))
        return usuario_login