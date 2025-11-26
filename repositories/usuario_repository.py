from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalars().first()
    
    async def get_by_email_docente_estudiante(self, email: str) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email, Usuario.type == 'estudiante')
        )
        return result.scalars().first()

    async def update(self, usuario: Usuario, update_data: dict) -> Usuario:
        for key, value in update_data.items():
            setattr(usuario, key, value)
        await self.db.commit()
        await self.db.refresh(usuario)
        return usuario