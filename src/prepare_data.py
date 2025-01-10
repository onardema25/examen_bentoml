import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

# Chemin d'accès au fichier CSV
DATA_PATH = "data/raw/admission.csv"
PROCESSED_PATH = "data/processed"

# Fonction principale pour préparer les données
def prepare_data():
    # Charger les données
    df = pd.read_csv(DATA_PATH)
    print(df.columns)

    # Supprimer les lignes contenant des valeurs manquantes
    df = df.dropna()
    # Supprimer les colonnes inutiles
    df = df.drop(columns=['Serial No.'])
   
    # Séparer les variables explicatives (X) et la cible (y)
    X = df.drop(columns=['Chance of Admit '])
    y = df['Chance of Admit ']

    # Diviser les données en jeux d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normaliser les variables explicatives
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Convertir les données normalisées en DataFrame pour sauvegarde
    X_train = pd.DataFrame(X_train_scaled, columns=X.columns)
    X_test = pd.DataFrame(X_test_scaled, columns=X.columns)

    # Créer le dossier de sauvegarde s'il n'existe pas
    os.makedirs(PROCESSED_PATH, exist_ok=True)

    # Sauvegarder les fichiers traités
    X_train.to_csv(os.path.join(PROCESSED_PATH, 'X_train.csv'), index=False)
    X_test.to_csv(os.path.join(PROCESSED_PATH, 'X_test.csv'), index=False)
    y_train.to_csv(os.path.join(PROCESSED_PATH, 'y_train.csv'), index=False)
    y_test.to_csv(os.path.join(PROCESSED_PATH, 'y_test.csv'), index=False)

    print("Les données ont été préparées et sauvegardées dans le dossier data/processed.")

if __name__ == "__main__":
    prepare_data()
