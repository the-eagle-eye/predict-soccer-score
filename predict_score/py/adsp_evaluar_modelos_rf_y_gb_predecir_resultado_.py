# -*- coding: utf-8 -*-
"""ADSP - EVALUAR MODELOS RF y GB - PREDECIR RESULTADO .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11KJAUf0WtUgp05oTCFQyxzonLkMdELuS
"""

# Importar librerías necesarias
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import numpy as np
import joblib

# List of URLs of the datasets
urls = [
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2122/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2021/E0.csv",
    "https://www.football-data.co.uk/mmz4281/1920/E0.csv",
]

"""## Cargar Datos"""

# Cargar todos los CSVs
dfs = [pd.read_csv(url) for url in urls]

# Visualizar las primeras filas de cada dataset para inspeccionar la estructura
for i, df in enumerate(dfs):
    print(f"DataFrame {i+1}:")
    print(df.head(), "\n")

"""## Unir DataFrames"""

# Unir todos los DataFrames en uno solo
matches = pd.concat(dfs, ignore_index=True)

# Verificar el tamaño del DataFrame combinado
print(matches.shape)

# Load and preprocess the dataset
def load_and_preprocess_data():
    # Create features
    matches['goal_difference'] = matches['FTHG'] - matches['FTAG']
    matches['HF'] = matches.groupby('HomeTeam')['goal_difference'].rolling(5).mean().reset_index(level=0, drop=True)
    matches['AF'] = matches.groupby('AwayTeam')['goal_difference'].rolling(5).mean().reset_index(level=0, drop=True)

    features = ['FTHG', 'FTAG', 'HS', 'AS', 'HST', 'AST', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR', 'HF', 'AF', 'HomeTeam', 'AwayTeam']
    matches.fillna(0, inplace=True)
    return matches, features

"""## train_test_split"""

# Prepare train/test split
def prepare_data(matches, features, target):
    X = matches[features]
    y = matches[target]

    X_train, X_test, y_train, y_test = train_test_split(X,y,random_state = 123, test_size = 0.2)

    return X_train, X_test, y_train, y_test

# Create preprocessing pipeline
def create_preprocessor():
    numeric_features = ['HF', 'AF']
    categorical_features = ['HomeTeam', 'AwayTeam']

    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    return preprocessor

# Train a Random Forest model
def train_random_forest(X_train, y_train):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

"""# Train a Random Forest model
def train_random_forest(X_train, y_train):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model
"""

# Predict match outcome
def predict_match(home_team, away_team, historical_matches, preprocessor, home_model, away_model):
    def calculate_average_form(team, matches, home_or_away):
        team_matches = matches[matches[f'{home_or_away}Team'] == team]
        if len(team_matches) < 5:
            return team_matches['goal_difference'].mean()
        return team_matches['goal_difference'].rolling(5).mean().iloc[-1]

    # Validate if teams exist in the dataset
    if home_team not in historical_matches['HomeTeam'].values and home_team not in historical_matches['AwayTeam'].values:
        print(f"Error: '{home_team}' does not exist in the dataset.")
        return None

    if away_team not in historical_matches['HomeTeam'].values and away_team not in historical_matches['AwayTeam'].values:
        print(f"Error: '{away_team}' does not exist in the dataset.")
        return None

    # Calculate team form
    home_team_form = calculate_average_form(home_team, historical_matches, 'Home') or 0
    away_team_form = calculate_average_form(away_team, historical_matches, 'Away') or 0

    # Prepare data for prediction
    new_match = pd.DataFrame({
        'HomeTeam': [home_team],
        'AwayTeam': [away_team],
        'HF': [home_team_form],
        'AF': [away_team_form]
    })

    new_match_preprocessed = preprocessor.transform(new_match)

    # Predict scores
    home_goals = round(home_model.predict(new_match_preprocessed)[0])
    away_goals = round(away_model.predict(new_match_preprocessed)[0])

    print(f'Predicted goals: {home_team} {home_goals} - {away_goals} {away_team}')

    if home_goals > away_goals:
        return f'{home_team} wins'
    elif home_goals < away_goals:
        return f'{away_team} wins'
    else:
        return 'Draw'

"""![image.png](data:image/png;base64,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)"""

# Main function
def main(home_team, away_team):
    # Load and preprocess data
    matches, features = load_and_preprocess_data()

    # Split data for home and away goal prediction
    X_train, X_test, y_home_train, y_home_test = prepare_data(matches, features, 'FTHG')
    _, _, y_away_train, y_away_test = prepare_data(matches, features, 'FTAG')

    # Preprocessing pipeline
    preprocessor = create_preprocessor()
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    # Train models
    home_goal_model = train_random_forest(X_train, y_home_train)
    away_goal_model = train_random_forest(X_train, y_away_train)

    # Import models to joblib
    joblib.dump(home_goal_model, 'modelo_gb_local.pkl')
    joblib.dump(away_goal_model, 'modelo_gb_visitante.pkl')

    # Evaluate models
    y_home_pred = home_goal_model.predict(X_test)
    y_away_pred = away_goal_model.predict(X_test)

    print(f'Home Goal Prediction RMSE: {np.sqrt(mean_squared_error(y_home_test, y_home_pred))}')
    print(f'Away Goal Prediction RMSE: {np.sqrt(mean_squared_error(y_away_test, y_away_pred))}')
    print(f'Home Goal Prediction MSE: {mean_squared_error(y_home_test, y_home_pred)}')
    print(f'Away Goal Prediction MSE: {mean_squared_error(y_away_test, y_away_pred)}')


    # Calcular métricas
    metrics = {
      "Model": ["Random Forest"],
      "MSE": [mean_squared_error(y_home_test, y_home_pred), [mean_squared_error(y_away_test, y_away_pred)]],
    }

    # Example prediction
    historical_matches = matches.copy()
    result = predict_match(home_team, away_team, historical_matches, preprocessor, home_goal_model, away_goal_model)
    print(f'Match prediction: {result}')

if __name__ == "__main__":
    main('Man City', 'Liverpool')

#### GRADIENT BOOSTING

from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

# Reemplazar la función de entrenamiento con Gradient Boosting
def train_gradient_boosting(X_train, y_train):
    """
    Entrena un modelo de Gradient Boosting utilizando XGBoost.
    Args:
        X_train (array): Características de entrenamiento.
        y_train (array): Etiquetas de entrenamiento.
    Returns:
        model: Modelo entrenado.
    """
    model = XGBRegressor(
        n_estimators=100,  # Número de árboles
        learning_rate=0.1,  # Tasa de aprendizaje
        max_depth=6,       # Profundidad máxima de los árboles
        subsample=0.8,     # Submuestreo de filas
        colsample_bytree=0.8,  # Submuestreo de columnas
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

# Main function adaptada para GB
def main(home_team, away_team):
    # Load and preprocess data
    matches, features = load_and_preprocess_data()

    # Split data for home and away goal prediction
    X_train, X_test, y_home_train, y_home_test = prepare_data(matches, features, 'FTHG')
    _, _, y_away_train, y_away_test = prepare_data(matches, features, 'FTAG')

    # Preprocessing pipeline
    preprocessor = create_preprocessor()
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    # Train Gradient Boosting models
    home_goal_model = train_gradient_boosting(X_train, y_home_train)
    away_goal_model = train_gradient_boosting(X_train, y_away_train)

    # Evaluate models
    y_home_pred = home_goal_model.predict(X_test)
    y_away_pred = away_goal_model.predict(X_test)

    # Evaluar el rendimiento utilizando RMSE
    home_rmse = np.sqrt(mean_squared_error(y_home_test, y_home_pred))
    home_mse = mean_squared_error(y_home_test, y_home_pred)
    away_rmse = np.sqrt(mean_squared_error(y_away_test, y_away_pred))
    away_mse = mean_squared_error(y_away_test, y_away_pred)
    print(f'Home Goal Prediction RMSE: {home_rmse}')
    print(f'Away Goal Prediction RMSE: {away_rmse}')
    print(f'Home Goal Prediction MSE: {home_mse}')
    print(f'Away Goal Prediction MSE: {away_mse}')
    # Example prediction
    historical_matches = matches.copy()
    result = predict_match(home_team, away_team, historical_matches, preprocessor, home_goal_model, away_goal_model)
    print(f'Match prediction: {result}')

# Llamada a la función principal
if __name__ == "__main__":
    main('Man City', 'Liverpool')

!python --version