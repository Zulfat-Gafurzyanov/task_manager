import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()


class Encryption:
    """Шифрование чувствительных полей (email, phone)."""
    _key: bytes | None = None

    @classmethod
    def _get_key(cls) -> bytes:
        """Получает ключ из окружения и декодирует из base64."""
        if cls._key is None:
            raw = os.environ['ENCRYPTION_KEY']
            if not raw:
                raise RuntimeError("ENCRYPTION_KEY не задан.")
            cls._key = base64.b64decode(raw)
            if len(cls._key) != 32:
                raise RuntimeError("ENCRYPTION_KEY должен быть 32 байта.")
        return cls._key

    @staticmethod
    async def encrypt_value(plain_text: str) -> str:
        """
        Шифрует строку. Возвращает base64-строку формата: nonce + ciphertext.
        """
        key = Encryption._get_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 12 байт.
        ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
        # Сохраняем nonce + ciphertext в одну строку, декодируем в base64.
        return base64.b64encode(nonce + ciphertext).decode("utf-8")

    @staticmethod
    async def decrypt_value(encrypted_text: str) -> str:
        """
        Расшифровывает строку, зашифрованную encrypt_value.
        """
        key = Encryption._get_key()
        aesgcm = AESGCM(key)
        raw = base64.b64decode(encrypted_text)
        nonce = raw[:12]
        ciphertext = raw[12:]
        plain_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        return plain_bytes.decode("utf-8")
