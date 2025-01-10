import bentoml
from bentoml.io import JSON
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

# Configuration JWT
JWT_SECRET_KEY = "your_secret_key"
JWT_ALGORITHM = "HS256"

# Charger le modèle sauvegardé
model_runner = bentoml.sklearn.get("admission_predictor:latest").to_runner()

# Définir le service BentoML
svc = bentoml.Service("admission_prediction_service", runners=[model_runner])

# Middleware d'authentification JWT
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/predict":
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})

            try:
                token = token.split()[1]  # Remove 'Bearer ' prefix
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token has expired"})
            except jwt.InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})

            request.state.user = payload.get("sub")

        response = await call_next(request)
        return response

# Ajouter le middleware au service FastAPI
svc.add_asgi_middleware(JWTAuthMiddleware)

# Données attendues pour la prédiction
class AdmissionInput(BaseModel):
    gre_score: float
    toefl_score: float
    university_rating: int
    sop: float
    lor: float
    cgpa: float
    research: int

# Endpoint de prédiction
@svc.api(input=JSON(pydantic_model=AdmissionInput), output=JSON())
def predict(input_data: AdmissionInput, request: Request):
    # Préparer les données pour le modèle
    data = [[
        input_data.gre_score,
        input_data.toefl_score,
        input_data.university_rating,
        input_data.sop,
        input_data.lor,
        input_data.cgpa,
        input_data.research,
    ]]

    # Effectuer la prédiction
    prediction = model_runner.run(data)

    # Retourner la prédiction
    return {"chance_of_admit": prediction[0]}

# Endpoint pour sécuriser l'accès avec un login simple
@svc.api(input=JSON(), output=JSON())
def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")

    if username != "user123" or password != "123":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Créer un token JWT
    token = jwt.encode({"sub": username}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return {"message": "Login successful", "token": token}
