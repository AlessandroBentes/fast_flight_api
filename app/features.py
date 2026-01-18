from datetime import datetime
from app.weather_features import aggregate_weather_1h
from app.cancel_rate import CancellationRate
import pandas as pd


# Horários de pico 
PEAK_HOURS = range(6, 10)  # 06h–09h - Verificar com Jesse

# Exemplo simples de feriados fixos (MM-DD)
HOLIDAYS = {"01-01", "12-25"} #Verificar com Jesse


def hour_to_bucket(hour: int) -> int:
    if 0 <= hour < 6:
        return 0  # madrugada
    elif 6 <= hour < 12:
        return 1  # manhã
    elif 12 <= hour < 18:
        return 2  # tarde
    else:
        return 3  # noite


def build_base_features(data) -> dict:
    """Constrói as features base a partir dos dados de entrada do voo."""
    dt = data.data_partida

    hour_bucket = hour_to_bucket(dt.hour)
    is_weekend = 1 if dt.weekday() >= 5 else 0
    is_peak_hour = 1 if dt.hour in PEAK_HOURS else 0

    date_key = dt.strftime("%m-%d")
    is_holiday = 1 if date_key in HOLIDAYS else 0

    is_long_weekend = 1 if is_holiday and is_weekend else 0

    return {
        "airline": data.companhia,
        "route": f"{data.origem}_{data.destino}",
        "hour_bucket": hour_bucket,
        "day_of_week": dt.weekday(),
        "month": dt.month,
        "is_peak_hour": is_peak_hour,
        "is_weekend": is_weekend,
        "is_holiday": is_holiday,
        "is_long_weekend": is_long_weekend,
    }

def enrich_with_cancellation_rates(features: dict, cancellation_service: CancellationRate) -> dict:
    """Adiciona features de taxas de cancelamento ao dicionário de features."""
    airline_code = features.get("airline")
    # Assumindo que a rota está no formato "ORIGEM_DESTINO"
    origin_code = features.get("route").split('_')[0]
    route_code = features.get("route")

    features["cancel_rate_airline_30d"] = cancellation_service.get_airline_cancel_rate(airline_code)
    features["cancel_rate_origin_30d"] = cancellation_service.get_origin_cancel_rate(origin_code)
    features["cancel_rate_route_30d"] = cancellation_service.get_route_cancel_rate(route_code)

    return features

def enrich_with_weather(features: dict, weather_df: pd.DataFrame) -> dict:
    """Adiciona features meteorológicas ao dicionário de features."""
    weather_features = aggregate_weather_1h(weather_df)
    features.update(weather_features)
    return features

def build_features(input_data, cancellation_service: CancellationRate, weather_df: pd.DataFrame) -> dict:
    """
    Constrói todas as features para a previsão de atraso de voo.
    """
    # 1. Constrói as features base
    features = build_base_features(input_data)

    # 2. Adiciona as taxas de cancelamento
    features = enrich_with_cancellation_rates(features, cancellation_service)

    # 3. Adiciona as features meteorológicas
    features = enrich_with_weather(features, weather_df)

    return features

