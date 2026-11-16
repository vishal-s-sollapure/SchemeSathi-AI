from typing import Optional
from sqlalchemy.orm import Session

from app.models.source import OfficialSource
from app.repositories.base import BaseRepository


class OfficialSourceRepository(BaseRepository[OfficialSource]):
    def __init__(self, db: Session):
        super().__init__(OfficialSource, db)

    def get_by_circular_number(self, circular_number: str) -> Optional[OfficialSource]:
        return self.db.query(OfficialSource).filter(OfficialSource.circular_number == circular_number).first()
