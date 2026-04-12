from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from api import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("api.get_channel")
def test_emit_log_success(mock_channel):
    mock_conn = MagicMock()
    mock_ch = MagicMock()
    mock_channel.return_value = (mock_conn, mock_ch)

    response = client.post("/logs", json={"message": "test log"})

    assert response.status_code == 200
    assert response.json()["status"] == "sent"
    assert response.json()["message"] == "test log"
    mock_ch.basic_publish.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("api.get_channel")
def test_emit_log_rabbitmq_error(mock_channel):
    mock_channel.side_effect = Exception("RabbitMQ unavailable")

    response = client.post("/logs", json={"message": "test log"})

    assert response.status_code == 500
    assert "RabbitMQ unavailable" in response.json()["detail"]


@patch("api.collection")
def test_get_logs_empty(mock_collection):
    mock_collection.find.return_value = []

    response = client.get("/logs")

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["logs"] == []


@patch("api.collection")
def test_get_logs_with_data(mock_collection):
    mock_collection.find.return_value = [
        {"message": "hello", "timestamp": None},
        {"message": "world", "timestamp": None},
    ]

    response = client.get("/logs")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["logs"][0]["message"] == "hello"


@patch("api.collection")
def test_delete_logs(mock_collection):
    mock_result = MagicMock()
    mock_result.deleted_count = 3
    mock_collection.delete_many.return_value = mock_result

    response = client.delete("/logs")

    assert response.status_code == 200
    assert response.json()["deleted"] == 3
