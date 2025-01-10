import pytest
import requests
import jwt
import time

BASE_URL = "http://localhost:4000"
LOGIN_ENDPOINT = f"{BASE_URL}/login"
PREDICT_ENDPOINT = f"{BASE_URL}/predict"
JWT_SECRET_KEY = "your_secret_key"
JWT_ALGORITHM = "HS256"

@pytest.fixture
def valid_credentials():
    return {"username": "user123", "password": "123"}

@pytest.fixture
def invalid_credentials():
    return {"username": "wrong_user", "password": "wrong_pass"}

@pytest.fixture
def valid_payload():
    return {
        "gre_score": 320,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.0,
        "cgpa": 9.2,
        "research": 1
    }

@pytest.fixture
def invalid_payload():
    return {
        "gre_score": "invalid",  # Non-numeric value
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.0,
        "cgpa": 9.2,
        "research": 1
    }

@pytest.fixture
def expired_token():
    payload = {"sub": "user123", "exp": time.time() - 10}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

@pytest.fixture
def valid_token():
    payload = {"sub": "user123", "exp": time.time() + 3600}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def test_login_valid_credentials(valid_credentials):
    response = requests.post(
        LOGIN_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json=valid_credentials
    )
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_invalid_credentials(invalid_credentials):
    response = requests.post(
        LOGIN_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json=invalid_credentials
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Unauthorized"

def test_authentication_missing_token(valid_payload):
    response = requests.post(
        PREDICT_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json=valid_payload
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Missing authentication token"

def test_authentication_invalid_token(valid_payload):
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.post(
        PREDICT_ENDPOINT,
        headers=headers,
        json=valid_payload
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Invalid token"

def test_authentication_expired_token(valid_payload, expired_token):
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = requests.post(
        PREDICT_ENDPOINT,
        headers=headers,
        json=valid_payload
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Token has expired"

def test_predict_valid_token(valid_payload, valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = requests.post(
        PREDICT_ENDPOINT,
        headers=headers,
        json=valid_payload
    )
    assert response.status_code == 200
    assert "chance_of_admit" in response.json()

def test_predict_invalid_payload(valid_payload, valid_token, invalid_payload):
    headers = {"Authorization": f"Bearer {valid_token}"}
    response = requests.post(
        PREDICT_ENDPOINT,
        headers=headers,
        json=invalid_payload
    )
    assert response.status_code == 422  # Expecting validation error
