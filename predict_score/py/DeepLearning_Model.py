# -*- coding: utf-8 -*-
"""Modelo-Usando-DeepLearning.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K4K7qV2XvrVZwdFiPA4aiYWgcbby6Fb7
"""

#### DEEP LEARNING

import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Paso 1: Cargar y preprocesar los datos
def load_and_preprocess_data():
    """
    Carga los datos históricos de partidos de fútbol desde URLs, realiza
    ingeniería de características y prepara las columnas relevantes para la predicción.

    - Se calculan estadísticas de forma reciente de los equipos locales y visitantes (HF y AF).
    - Se agregan nuevas columnas derivadas como la diferencia de goles.
    - Se seleccionan las características principales y las columnas objetivo.

    Returns:
        matches (DataFrame): Datos preprocesados.
        features (list): Lista de columnas de entrada.
        targets (list): Lista de columnas objetivo ('FTHG', 'FTAG').
    """
    urls = [
        "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2122/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2021/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1920/E0.csv"
    ]
    dfs = [pd.read_csv(url) for url in urls]
    matches = pd.concat(dfs, ignore_index=True)

    # Ingeniería de características
    matches['goal_difference'] = matches['FTHG'] - matches['FTAG']
    matches['HF'] = matches.groupby('HomeTeam')['goal_difference'].rolling(5).mean().reset_index(level=0, drop=True)
    matches['AF'] = matches.groupby('AwayTeam')['goal_difference'].rolling(5).mean().reset_index(level=0, drop=True)
    matches.fillna(0, inplace=True)

    features = ['HF', 'AF', 'HomeTeam', 'AwayTeam']
    targets = ['FTHG', 'FTAG']  # Predicciones para ambos equipos
    return matches, features, targets

# Paso 2: Preprocesar las características
def preprocess_features(matches, features, targets):
    """
    Prepara los datos para el modelo: normaliza los datos numéricos y
    convierte las columnas categóricas a codificaciones one-hot.

    Returns:
        X_preprocessed (numpy array): Matriz de características transformadas.
        y (DataFrame): Valores objetivo.
        preprocessor (ColumnTransformer): Objeto que encapsula las transformaciones aplicadas.
    """
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

    X = matches[features]
    y = matches[targets]

    X_preprocessed = preprocessor.fit_transform(X)
    return X_preprocessed, y, preprocessor

# Paso 3: Construir el modelo
def build_mlp(input_dim):
    """
    Define y compila una red neuronal multi-capa (MLP) para predecir
    los goles de los equipos local y visitante.

    - Tiene tres capas ocultas totalmente conectadas (dense).
    - Incluye dropout para reducir el sobreajuste.

    Args:
        input_dim (int): Dimensión de entrada.

    Returns:
        model (Sequential): Modelo MLP compilado.
    """
    model = Sequential([
        Dense(128, activation='relu', input_dim=input_dim),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(2)  # Dos salidas: una para cada equipo
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error', metrics=['mse'])
    return model

# Paso 4: Predecir goles para un nuevo partido
def predict_score(preprocessor, model, home_team, away_team):
    """
    Realiza una predicción para un nuevo partido entre dos equipos dados.

    Args:
        preprocessor (ColumnTransformer): Objeto preprocesador para transformar las características.
        model (Sequential): Modelo entrenado.
        home_team (str): Nombre del equipo local.
        away_team (str): Nombre del equipo visitante.

    Returns:
        predictions (array): Goles predichos para el equipo local y visitante.
    """
    new_match = pd.DataFrame({
        'HF': [1.5],  # Ejemplo de forma
        'AF': [1.2],
        'HomeTeam': [home_team],
        'AwayTeam': [away_team]
    })
    new_match_preprocessed = preprocessor.transform(new_match)
    predictions = model.predict(new_match_preprocessed)
    return predictions[0]

# Paso 5: Función principal para ejecutar el pipeline completo
def main():
    """
    Orquesta todo el flujo de trabajo:
    - Carga y preprocesa los datos.
    - Divide los datos en entrenamiento y prueba.
    - Entrena el modelo de red neuronal.
    - Evalúa el rendimiento del modelo.
    - Predice un partido de ejemplo entre dos equipos.
    """
    # Cargar y preprocesar datos
    matches, features, targets = load_and_preprocess_data()
    X, y, preprocessor = preprocess_features(matches, features, targets)

    # Dividir en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

    # Crear y entrenar modelo
    input_dim = X_train.shape[1]
    model = build_mlp(input_dim)
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, verbose=1)

    # Evaluar modelo
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")

    # Guardar el modelo
    model.save("mlp_score_predictor.h5")

    # Predecir ejemplo
    home_team = 'Man City'
    away_team = 'Liverpool'
    predicted_scores = predict_score(preprocessor, model, home_team, away_team)
    print(f"Predicted score - {home_team}: {predicted_scores[0]:.2f}, {away_team}: {predicted_scores[1]:.2f}")

if __name__ == "__main__":
    main()