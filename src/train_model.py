import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import bentoml
import os

# Chemins d'accès aux données
PROCESSED_PATH = "data/processed"

# Fonction principale pour entraîner le modèle
def train_model():
    # Charger les données traitées
    X_train = pd.read_csv(os.path.join(PROCESSED_PATH, 'X_train.csv'))
    X_test = pd.read_csv(os.path.join(PROCESSED_PATH, 'X_test.csv'))
    y_train = pd.read_csv(os.path.join(PROCESSED_PATH, 'y_train.csv'))
    y_test = pd.read_csv(os.path.join(PROCESSED_PATH, 'y_test.csv'))

    # Créer un modèle de régression linéaire
    model = LinearRegression()

    # Entraîner le modèle sur les données d'entraînement
    model.fit(X_train, y_train.values.ravel())

    # Prédire sur les données de test
    y_pred = model.predict(X_test)

    # Évaluer les performances du modèle
    r2 = r2_score(y_test, y_pred)

    print(f"Performances du modèle:\nR2: {r2:.4f}")

    # Sauvegarder le modèle dans le Model Store de BentoML
    bentoml.sklearn.save_model("admission_predictor", model)
    print("Modèle sauvegardé dans le Model Store de BentoML.")

if __name__ == "__main__":
    train_model()
