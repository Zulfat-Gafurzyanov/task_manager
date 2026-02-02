# task_manager

## Создание ENCRYPTION_KEY:
python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"