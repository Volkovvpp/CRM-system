from passlib.context import CryptContext

# Настраиваем контекст шифрования с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Превращает "qwerty1234" в "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq"
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Сравнивает введенный пароль с хэшем из базы данных.
        Возвращает True или False.
        """
        return pwd_context.verify(plain_password, hashed_password)