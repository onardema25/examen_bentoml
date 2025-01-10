import pytest
import requests

BASE_URL = "http://localhost:4000"
LOGIN_ENDPOINT = f"{BASE_URL}/login"
PREDICT_ENDPOINT = f"{BASE_URL}/predict"

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

def test_login_valid_credentials(valid_credentials):
    response = requests.post(LOGIN_ENDPOINT, json=valid_credentials)
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Login successful"

def test_login_invalid_credentials(invalid_credentials):
    response = requests.post(LOGIN_ENDPOINT, json=invalid_credentials)
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Unauthorized"

def test_predict_valid_payload(valid_credentials, valid_payload):
    # Authenticate and get token
    login_response = requests.post(LOGIN_ENDPOINT, json=valid_credentials)
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json().get('token', '')}"}

    # Test prediction endpoint
    response = requests.post(PREDICT_ENDPOINT, json=valid_payload, headers=headers)
    assert response.status_code == 200
    assert "chance_of_admit" in response.json()

def test_predict_invalid_payload(valid_credentials, invalid_payload):
    # Authenticate and get token
    login_response = requests.post(LOGIN_ENDPOINT, json=valid_credentials)
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json().get('token', '')}"}

    # Test prediction endpoint with invalid payload
    response = requests.post(PREDICT_ENDPOINT, json=invalid_payload, headers=headers)
    assert response.status_code != 200  # Expecting an error

def test_predict_missing_token(valid_payload):
    # Test prediction endpoint without authentication
    response = requests.post(PREDICT_ENDPOINT, json=valid_payload)
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Unauthorized"
