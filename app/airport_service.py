import pandas as pd
import httpx

class AirportService:
    def __init__(self, csv_path: str, api_key: str):
        self.df = pd.read_csv(csv_path)
        self.df["airport_code"] = self.df["airport_code"].astype(str).str.upper()
        self.airports = {
            row["airport_code"]: {
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
            }
            for _, row in self.df.iterrows()
        }
        self.api_key = api_key


    def get_coordinates_archive(self, ident: str):
        code = ident.upper()

        if code not in self.airports:
            raise ValueError("Aeroporto {code} não encontrado no CSV")

        return self.airports[code]
    
    

    def get_coordinates_online(self, airport_code: str):
        url = f"https://aeroapi.flightaware.com/aeroapi/airports/{airport_code}"
        
        headers = {
            "Accept": "application/json; charset=UTF-8",
            "x-apikey": self.api_key
        }
        
        try:
            
            #async with httpx.AsyncClient(timeout=10) as client:

                #response = await client.get(url, headers=headers)
                response = httpx.get(url, headers=headers) 
                response.raise_for_status()  # Levanta um erro para respostas não 2xx
                data = response.json()
                
                latitude = data['latitude']
                longitude = data['longitude']
                
                return {"latitude": latitude, "longitude": longitude}
                
        except httpx.RequestError as exc:
            print(f"Erro ao solicitar dados do aeroporto: {exc}")
            return None
        except httpx.HTTPStatusError as exc:
            print(f"Erro na resposta: {exc.response.status_code} - {exc.response.text}")
            return None
        except KeyError:
            print("Dados de latitude e longitude não encontrados na resposta.")
            return None

# Exemplo de uso
#if __name__ == "__main__":
#    airport_code = "GIG"  # Código do aeroporto
#    api_key = "XXXXXXXXXXXXXXXXXXXXX"  # Substitua pela sua chave de API
#
#    coords = get_airport_coordinates(airport_code, api_key)
#    if coords:
#        print(f"Coordenadas do aeroporto {airport_code}: Latitude {coords[0]}, Longitude {coords[1]}")

