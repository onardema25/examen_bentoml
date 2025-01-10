import bentoml
from bentoml.io import JSON
from pydantic import BaseModel
from fastapi import HTTPException

# Charger le modèle sauvegardé
model_runner = bentoml.sklearn.get("admission_predictor:latest").to_runner()

# Définir le service BentoML
svc = bentoml.Service("admission_prediction_service", runners=[model_runner])

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
def predict(input_data: AdmissionInput):
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

    if username == "user123" and password == "123":
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
