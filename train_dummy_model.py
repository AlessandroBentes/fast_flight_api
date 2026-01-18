import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


# =========================
# 1. Geração de dados fictícios
# =========================

def generate_dummy_data(n_samples: int = 3000) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    airlines = ["AZ", "LA", "G3", "AD"]
    routes = ["SBGL_SBGR", "SBGR_SBCF", "SBBR_SBGL", "SBCF_SBGR"]
    # Para simular dados de origem para as taxas de cancelamento de origem
    origins = ["SBGL", "SBGR", "SBBR", "SBCF"] 

    data = {
        "airline": rng.choice(airlines, n_samples),
        "route": rng.choice(routes, n_samples),

        "hour_bucket": rng.integers(0, 4, n_samples),
        "day_of_week": rng.integers(0, 7, n_samples),
        "month": rng.integers(1, 13, n_samples),

        "is_peak_hour": rng.integers(0, 2, n_samples),
        "is_weekend": rng.integers(0, 2, n_samples),
        "is_holiday": rng.integers(0, 2, n_samples),
        "is_long_weekend": rng.integers(0, 2, n_samples),

        "wind_max_1h": rng.normal(10, 4, n_samples).clip(0),
        "cloud_mean_1h": rng.uniform(0, 100, n_samples),
        "rain_sum_1h": rng.exponential(1.2, n_samples),
        "snow_sum_1h": rng.exponential(0.1, n_samples),
        
        # === NOVAS FEATURES DE CANCELAMENTO ===
        # Gerando valores aleatórios entre 0.05 e 0.4 para simular taxas de cancelamento
        "cancel_rate_airline_30d": rng.uniform(0.05, 0.4, n_samples),
        "cancel_rate_origin_30d": rng.uniform(0.05, 0.4, n_samples),
        "cancel_rate_route_30d": rng.uniform(0.05, 0.4, n_samples),
        # ======================================
    }

    df = pd.DataFrame(data)

    # Regra sintética para atraso (target) - você pode ajustar esta regra
    # para incluir as novas features, se desejar uma correlação no dummy data.
    # Por exemplo: (df["cancel_rate_route_30d"] > 0.3).astype(int)
    df["delay"] = (
        (df["rain_sum_1h"] > 2.5).astype(int)
        | (df["wind_max_1h"] > 15).astype(int)
        | (df["cloud_mean_1h"] > 80).astype(int)
        | ((df["is_peak_hour"] == 1) & (df["is_weekend"] == 0))
    ).astype(int)

    return df


# =========================
# 2. Treinamento do modelo
# =========================

def train_model(df: pd.DataFrame):

    categorical_features = ["airline", "route"]
    numeric_features = [
        "hour_bucket",
        "day_of_week",
        "month",
        "is_peak_hour",
        "is_weekend",
        "is_holiday",
        "is_long_weekend",
        "wind_max_1h",
        "cloud_mean_1h",
        "rain_sum_1h",
        "snow_sum_1h",
        # === NOVAS FEATURES NUMÉRICAS ===
        "cancel_rate_airline_30d",
        "cancel_rate_origin_30d",
        "cancel_rate_route_30d",
        # ================================
    ]

    X = df[categorical_features + numeric_features]
    y = df["delay"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)

    score = pipeline.score(X_test, y_test)
    print(f"Acurácia (dummy): {score:.2f}")

    return pipeline


# =========================
# 3. Execução
# =========================

if __name__ == "__main__":
    print("Gerando dados fictícios...")
    df = generate_dummy_data()

    print("Treinando modelo...")
    model = train_model(df)

    print("Salvando modelo em model/BestLogReg.joblib")
    # Certifique-se de que a pasta 'model' existe
    joblib.dump(model, "model/BestLogReg.joblib")

    print("Treinamento concluído com sucesso.")
