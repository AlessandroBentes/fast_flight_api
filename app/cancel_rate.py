# app/cancel_rate.py
import pandas as pd
from typing import Dict

class CancellationRate:
    def __init__(self, airline_csv_file_path: str, origin_csv_file_path: str, route_csv_file_path: str):
        # Carrega os CSVs na inicialização e os armazena como dicionários para busca rápida
        self.airline_rates = self._load_rates(airline_csv_file_path, 'airline', 'cancel_rate_airline_30d')
        self.origin_rates = self._load_rates(origin_csv_file_path, 'origin', 'cancel_rate_origin_30d')
        self.route_rates = self._load_rates(route_csv_file_path, 'route', 'cancel_rate_route_30d')

    def _load_rates(self, file_path: str, key_col: str, rate_col: str) -> Dict[str, float]:
        """
        Carrega um arquivo CSV e retorna um dicionário de taxas.
        Espera que o CSV tenha uma coluna 'key_col' e uma coluna 'rate_col'.
        """
        try:
            df = pd.read_csv(file_path)
            if key_col not in df.columns or rate_col not in df.columns:
                print(f"Erro: Colunas '{key_col}' ou '{rate_col}' não encontradas em {file_path}")
                return {}
            # Converte para maiúsculas para correspondência consistente
            df[key_col] = df[key_col].astype(str).str.upper()
            # Cria um dicionário para busca rápida, preenchendo NaN com 0.0
            return df.set_index(key_col)[rate_col].fillna(0.0).to_dict()
        except FileNotFoundError:
            print(f"Erro: O arquivo {file_path} não foi encontrado.")
            return {}
        except Exception as e:
            print(f"Ocorreu um erro ao ler o arquivo {file_path}: {e}")
            return {}

    def get_airline_cancel_rate(self, airline_code: str) -> float:
        """Retorna a taxa de cancelamento da companhia aérea."""
        return self.airline_rates.get(airline_code.upper(), 0.0) # Assume códigos em maiúsculas

    def get_origin_cancel_rate(self, origin_code: str) -> float:
        """Retorna a taxa de cancelamento do aeroporto de origem."""
        return self.origin_rates.get(origin_code.upper(), 0.0) # Assume códigos em maiúsculas

    def get_route_cancel_rate(self, route_code: str) -> float:
        """Retorna a taxa de cancelamento da rota."""
        return self.route_rates.get(route_code.upper(), 0.0) # Assume códigos em maiúsculas
