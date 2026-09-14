from fastapi.testclient import TestClient
from app.utils.exceptions import LLMError, MemoryError
from app.main import app


client = TestClient(app,raise_server_exceptions=False)


def test_chat_success():
    response = client.post(
        "/chat",
        json={
            "user_id": "test001",
            "query": "推荐一台三星手机，预算4000元"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "requirements" in data
    assert "products" in data

    assert isinstance(data["products"], list)

def test_chat_missing_query():
    response = client.post(
        "/chat",
        json={
            "user_id": "test001"
        }
    )

    assert response.status_code == 422

def test_chat_e2e_product_filter():
    response = client.post(
        "/chat",
        json={
            "user_id": "test001",
            "query": "推荐三星手机，预算4000元"
        }
    )

    assert response.status_code == 200

    data = response.json()

    for product in data["products"]:
        assert product["brand"] == "Samsung"
        assert product["price"] <= 4000

def test_chat_llm_error(monkeypatch):
    async def mock_create_agent():
        raise LLMError("LLM timeout")

    monkeypatch.setattr(
        "app.main.create_agent",
        mock_create_agent
    )

    response = client.post(
        "/chat",
        json={
            "user_id": "test001",
            "query": "推荐一台手机"
        }
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI 服务暂时不可用，请稍后重试"

def test_chat_memory_error(monkeypatch):
    async def mock_create_agent():
        raise MemoryError("Database connection failed")

    monkeypatch.setattr(
        "app.main.create_agent",
        mock_create_agent
    )

    response = client.post(
        "/chat",
        json={
            "user_id": "test001",
            "query": "推荐一台手机"
        }
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "记忆服务暂时不可用，请稍后重试"

def test_chat_unexpected_error(monkeypatch):
    async def mock_create_agent():
        raise RuntimeError("Something went wrong")

    monkeypatch.setattr(
        "app.main.create_agent",
        mock_create_agent
    )

    response = client.post(
        "/chat",
        json={
            "user_id": "test001",
            "query": "推荐一台手机"
        }
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "服务器内部错误"