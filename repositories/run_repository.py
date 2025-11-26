from models.run import Run
from sqlalchemy.ext.asyncio import AsyncSession

class RunRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_run(self, data: dict):
        nueva_run = Run(**data)
        self.db.add(nueva_run)
        await self.db.commit()
        await self.db.refresh(nueva_run)
        return nueva_run
