from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityConflictException, EntityNotFoundException
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_user(self, user_id: str) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.repo.list(skip=skip, limit=limit)

    def create_user(self, data: UserCreate) -> User:
        if data.email and self.repo.get_by_email(data.email):
            raise EntityConflictException(f"User with email '{data.email}' already exists.")
        if data.phone_number and self.repo.get_by_phone(data.phone_number):
            raise EntityConflictException(f"User with phone '{data.phone_number}' already exists.")
        
        user = User(
            full_name=data.full_name,
            email=data.email,
            phone_number=data.phone_number,
            role=data.role,
        )
        return self.repo.create(user)

    def update_user(self, user_id: str, data: UserUpdate) -> User:
        user = self.get_user(user_id)
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
        return self.repo.update(user)

    def delete_user(self, user_id: str) -> None:
        user = self.get_user(user_id)
        self.repo.delete(user)
