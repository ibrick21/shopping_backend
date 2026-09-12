from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User
from .orm_models import UserDB


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def _user_db_to_user(self, user_db: UserDB) -> User:

        user = User(
            name = user_db.name,
            user_id = user_db.user_id,
            email = user_db.email,
            password_hash = user_db.password_hash
        )

        return user
    
    def find_user(self, user_id: int):  
        user_db = self.session.get(UserDB, user_id)

        if user_db is None:
            return None

        return self._user_db_to_user(user_db)
    
    def add_user(self, user: User):
        user_db = UserDB(
            name = user.name,
            email = user.email,
            password_hash = user.password_hash
        )

        self.session.add(user_db)
        self.session.flush()

        user.user_id = user_db.user_id

        return user

    def find_by_email(self, email: str):
        stmt = select(UserDB).where(
            UserDB.email == email
    )
        user_db = self.session.scalar(stmt)

        if user_db is None:
            return None

        return self._user_db_to_user(user_db)
        