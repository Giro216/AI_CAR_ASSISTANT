from typing import Generic, TypeVar, Type, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get(self, id: any) -> Optional[ModelType]:
        return await self.db_session.get(self.model, id)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        self.db_session.add(obj)
        await self.db_session.flush()
        return obj

    async def delete(self, id: any) -> Optional[ModelType]:
        obj = await self.get(id)
        if obj:
            await self.db_session.delete(obj)
            await self.db_session.flush()
        return obj