import anyio
from fastapi import APIRouter, status
from fastapi import FastAPI, HTTPException
from app.schemas import (FlightInput, PredictionOutput,)
from app.features import build_features, enrich_with_weather
from app.model import FlightDelayModel
from app.weather_client import WeatherClient
from app.airport_service import AirportService
from app.cancel_rate import CancellationRate
from pathlib import Path
import traceback
import asyncio
import os


API_KEY = os.environ.get('MY_AEROAPI_KEY')
BASE_DIR = Path(__file__).resolve().parent.parent
AIRPORT_PATH = BASE_DIR / "data" / "airports_lat_lon.csv"
AIRLINE_CANCEL_RATE_PATH = BASE_DIR / "data" / "ops_airline.csv"
ORIGIN_CANCEL_RATE_PATH = BASE_DIR / "data" / "ops_origin.csv"
ROUTE_CANCEL_RATE_PATH = BASE_DIR / "data" / "ops_route.csv"

model = FlightDelayModel()
weather_client = WeatherClient()
airport_service = AirportService(AIRPORT_PATH, API_KEY)
cancellation_service = CancellationRate(airline_csv_file_path=AIRLINE_CANCEL_RATE_PATH, origin_csv_file_path=ORIGIN_CANCEL_RATE_PATH, route_csv_file_path=ROUTE_CANCEL_RATE_PATH)

router = APIRouter(
    prefix='/api/predict',
    tags=['predict'],
)


@router.post(path="/", response_model=PredictionOutput, status_code=status.HTTP_201_CREATED)
 
async def predict_flight_delay(input: FlightInput):
    
    try:  
        try:
            coords = airport_service.get_coordinates_archive(input.origem)
            if coords is None:
                raise HTTPException(status_code=404, detail=f"Coordenadas do aeroporto {input.origem} não encontradas.")
        except HTTPException: # Re-raise HTTPException
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado ao obter coordenadas do aeroporto: {e}")

        weather_df = await anyio.to_thread.run_sync(
        weather_client.get_weather_1h,        # A função a ser chamada
        coords["lat"],                        # Primeiro argumento posicional
        coords["lon"],                        # Segundo argumento posicional
        input.data_partida                    # Terceiro argumento posicional
        )
        
        #final_features = enrich_with_weather(base_features, weather_json)
        final_features = build_features(input, cancellation_service, weather_df)
    
        prediction_result = model.predict(final_features)

        previsao_str = prediction_result["prediction"]
        probabilidade_float = prediction_result["probability"]


        return {
            "previsao": previsao_str,
            "probabilidade": probabilidade_float
        }
    
    except HTTPException: # Re-lança qualquer HTTPException que já tenha sido gerado
        raise
    except Exception as e: # Captura qualquer outra exceção inesperada
        print(f"\n--- Erro GENÉRICO não tratado na rota predict_flight_delay ---")
        print(f"Tipo de erro: {type(e).__name__}")
        print(f"Mensagem: {e}")
        print(traceback.format_exc()) # Isso imprimirá o traceback completo
        print(f"----------------------------------------------------------\n")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")

#model = None
#@router.on_event("startup")
#def load_model():
#    global model
#    model = FlightDelayModel()
