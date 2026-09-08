from .models import User
from .user_repository import UserRepository
from .security import hash_password
from .exceptions import UserExistError

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

 
    def sign_up(self, name: str, email: str, password: str):
        user = self.user_repository.find_by_email(email)

        if user is not None:
            raise UserExistError
                    
        hashed_password = hash_password(password)

        user = User(
            name = name,
            email = email,
            password_hash = hashed_password
        )

        self.user_repository.add_user(user)

        return user