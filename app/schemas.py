from pydantic import BaseModel
from datetime import datetime

class FlightInput(BaseModel):
    companhia: str
    origem: str
    destino: str
    data_partida: datetime


class PredictionOutput(BaseModel):
    previsao: str
    probabilidade: float

