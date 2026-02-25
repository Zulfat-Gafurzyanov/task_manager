from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=131072,
    argon2__parallelism=4,
    argon2__time_cost=3,
)


def get_password_hash(password: str) -> str:
    """Хеширует пароль с использованием Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)
