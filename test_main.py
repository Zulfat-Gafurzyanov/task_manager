from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_task():
    task = {
        "name": "task for test",
        "description": "description for test",
        "deadline": "2026-12-31T02:06:16.662Z"
    }
    response = client.post("/api/v1/tasks", json=task)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == task["name"]
    assert data["description"] == task["description"]
    assert "deadline" in data and isinstance(data["deadline"], str)
    # ??? Не понимаю как проверить deadline == datetime.timezone(utc)


def test_get_tasks():
    """Тестирует получение списка задач."""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_task():
    response = client.get("/api/v1/tasks/1")
    assert response.status_code == 200
    assert response.status_code == 200 or 404
    # Наверно такой проверки недостаточно!?

# ??? Дальше не стал писать. Нужны твои советы по тестированию.
