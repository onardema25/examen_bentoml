import bentoml
from bentoml.io import JSON
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
from datetime import datetime, timedelta

# Configuration JWT
JWT_SECRET_KEY = "your_jwt_secret_key_here"
JWT_ALGORITHM = "HS256"

# Utilisateur défini
USER = {"username": "user123", "password": "123"}

# Middleware d'authentification JWT
class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/predict":
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})

            try:
                token = token.split()[1]  # Retirer le préfixe 'Bearer '
                jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token has expired"})
            except jwt.InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        response = await call_next(request)
        return response

# Modèle d'entrée pour la prédiction
class AdmissionInput(BaseModel):
    gre_score: float
    toefl_score: float
    university_rating: int
    sop: float
    lor: float
    cgpa: float
    research: int

# Charger le modèle sauvegardé
admission_runner = bentoml.sklearn.get("admission_predictor:latest").to_runner()

# Définir le service BentoML
svc = bentoml.Service("admission_prediction_service", runners=[admission_runner])

# Ajouter le middleware JWT
svc.add_asgi_middleware(JWTAuthMiddleware)

# Endpoint pour l'authentification
@svc.api(input=JSON(), output=JSON())
def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")

    if username == USER["username"] and password == USER["password"]:
        token = create_jwt_token(username)
        return {"token": token}
    else:
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

# Endpoint pour les prédictions
@svc.api(input=JSON(pydantic_model=AdmissionInput), output=JSON())
async def predict(input_data: AdmissionInput):
    data = [[
        input_data.gre_score,
        input_data.toefl_score,
        input_data.university_rating,
        input_data.sop,
        input_data.lor,
        input_data.cgpa,
        input_data.research
    ]]
    prediction = await admission_runner.predict.async_run(data)
    return {"chance_of_admit": prediction[0]}

# Fonction pour créer un token JWT
def create_jwt_token(user_id: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token
