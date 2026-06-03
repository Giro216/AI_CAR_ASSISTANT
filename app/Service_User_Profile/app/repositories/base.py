from typing import Generic, TypeVar, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get(self, id: any) -> Optional[ModelType]:
        return await self.db_session.get(self.model, id)

    async def create(self, obj: ModelType) -> ModelType:
        self.db_session.add(obj)
        await self.db_session.flush()
        return obj