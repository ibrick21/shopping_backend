from .exceptions import InvalidCredentialsError, UserExistError
from .models import User
from .security import create_access_token, hash_password, verify_password
from .user_repository import UserRepository


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

    def login(self, email: str, password: str):
        user = self.user_repository.find_by_email(email)

        if user is None:
            raise InvalidCredentialsError("로그인 실패")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("로그인 실패")


        token = create_access_token(user.user_id)
        return token 