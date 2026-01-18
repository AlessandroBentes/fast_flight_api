import pandas as pd

def aggregate_weather_1h(weather_df: pd.DataFrame) -> dict:
    """
    Agrega as features climáticas de um DataFrame de dados horários.
    Assume que o DataFrame contém dados para o período relevante (e.g., a última hora).
    """
    if weather_df.empty:
        return {
            "wind_max_1h": 0.0,
            "cloud_mean_1h": 0.0,
            "rain_sum_1h": 0.0,
            "snow_sum_1h": 0.0,
        }

    # Calcula as agregações sobre o DataFrame.
    # Se o DataFrame contiver apenas uma linha (um único forecast horário),
    # .max(), .mean(), .sum() simplesmente retornarão esse valor.
    return {
        "wind_max_1h": weather_df["windspeed_10m"].max(),
        "cloud_mean_1h": weather_df["cloudcover"].mean(),
        "rain_sum_1h": weather_df["rain"].sum(),
        "snow_sum_1h": weather_df["snowfall"].sum(),
    }
