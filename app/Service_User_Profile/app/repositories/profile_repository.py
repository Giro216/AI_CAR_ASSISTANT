from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Profile
from app.repositories.base import BaseRepository

class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Profile, db_session)