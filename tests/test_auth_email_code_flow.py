from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_request_code_and_verify_email_login_flow():
    response = client.post(
        "/auth/request-code",
        json={"email": "talento@ecodes.com", "role": "Talento Humano"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"].lower().startswith("se ha enviado")

    verify = client.post(
        "/auth/verify-code",
        json={"email": "talento@ecodes.com", "code": "123456", "role": "Talento Humano"},
    )
    assert verify.status_code == 200
    body = verify.json()
    assert "access_token" in body
    assert body["role"] == "Talento Humano"


def test_nonexistent_email_is_rejected():
    response = client.post(
        "/auth/request-code",
        json={"email": "noexiste@ecodes.com", "role": "Talento Humano"},
    )
    assert response.status_code == 404
