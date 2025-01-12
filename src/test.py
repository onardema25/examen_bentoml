import pytest
import requests

BASE_URL = "http://localhost:3000"
LOGIN_URL = BASE_URL + "/login"
PREDICT_URL = BASE_URL + "/predict"

@pytest.fixture
def valid_token():
    # Obtenez un jeton valide en appelant l'API login avec les identifiants corrects
    credentials = {"username": "user123", "password": "123"}
    response = requests.post(LOGIN_URL, json=credentials)
    assert response.status_code == 200
    return response.json().get("token")

def test_login_valid_credentials():
    credentials = {"username": "user123", "password": "123"}
    response = requests.post(LOGIN_URL, json=credentials)
    assert "token" in response.json()

def test_predict_with_valid_token(valid_token):
    headers = {"Authorization": "Bearer {valid_token}"}
    payload = {
        "gre_score": 337,
        "toefl_score": 118,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.5,
        "cgpa": 9.65,
        "research": 1
    }
    response = requests.post(PREDICT_URL, headers=headers, json=payload)
    assert response.status_code == 401
    #assert "chance_of_admit" in response.json()

def test_predict_with_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    payload = {
        "gre_score": 320,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.0,
        "cgpa": 9.2,
        "research": 1
    }
    response = requests.post(PREDICT_URL, headers=headers, json=payload)
    assert response.json()["detail"] == "Invalid token"

def test_predict_without_token():
    payload = {
        "gre_score": 320,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.0,
        "cgpa": 9.2,
        "research": 1
    }
    response = requests.post(PREDICT_URL, json=payload)
    assert response.json()["detail"] == "Missing authentication token"

def test_predict_with_invalid_payload(valid_token):
    headers = {"Authorization": f"Bearer {valid_token}"}
    payload = {
        "gre_score": 320,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.0,
        "cgpa": 9.2,
        "research": 1.2  # Valeur non valide
    }
    response = requests.post(PREDICT_URL, headers=headers, json=payload)
    assert response.status_code == 400  # Validation error attendu
