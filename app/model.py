from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "artefato_atraso_voos_rf.joblib"


class FlightDelayModel:
    def __init__(self):
        print(f"--- Tentando carregar modelo de: {MODEL_PATH} ---")
        try:
            self.model = joblib.load(MODEL_PATH)
            print(f"--- Modelo carregado com sucesso. Tipo: {type(self.model)} ---") # <--- ADICIONE ESTA LINHA
        except Exception as e:
            print(f"--- ERRO ao carregar o modelo: {e} ---")
            print("--- Certifique-se de que o arquivo 'BestLogReg.joblib' é um modelo válido ---")
            # Se o carregamento falhar, para evitar o AttributeError posterior,
            # podemos inicializar self.model com algo que falhe cedo.
            self.model = None # Ou raise um erro mais específico aqui.
    
    def predict(self, features: dict) -> dict:
        
        modelo = self.model["pipeline"]
        threshold = self.model["threshold"]

        if self.model is None: # Verificação para o caso de o carregamento ter falhado
            raise RuntimeError("O modelo não foi carregado corretamente na inicialização.")
        
        
        df = pd.DataFrame([features])

        #prob_atraso = self.model.predict_proba(df)[0][1]
        #prob_atraso = modelo.predict_proba(df)[0]
        proba_0, proba_1 = modelo.predict_proba(df)[0]

        # Classe mais provável
        if proba_1 > proba_0:
            prediction = 1
            probability = proba_1
        else:
            prediction = 0
            probability = proba_0


        #previsao = "Atrasado" if prob_atraso >= 0.5 else "Pontual"
        #previsao = int(prob_atraso >= threshold)
        
        previsao = "Atrasado" if prediction == 1 else "Pontual"
        #return previsao, float(prob_atraso)

        return {
                "prediction": previsao,
                "probability": float(probability)
        }
