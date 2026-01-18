# FastAPI Flight Delay Prediction Microservice

Um microserviço Python robusto construído com FastAPI para prever se um voo decolará no horário ("Pontual") ou com atraso ("Atrasado"), fornecendo também uma probabilidade associada à previsão. A solução integra múltiplos fatores, incluindo detalhes do voo, condições meteorológicas em tempo real e taxas históricas de cancelamento.

# Visão Geral do Projeto:
Este projeto demonstra a construção de um microserviço de inferência de Machine Learning (ML) performático e escalável. Ele expõe um endpoint /api/predict/ que recebe dados de um voo e, através de um pipeline de features complexo e um modelo de ML pré-treinado, retorna uma estimativa do status do voo.

# Arquitetura de Alto Nível:

## API Java
##       ↓
## [ FastAPI Microservice ]
##    ↓
##    ├── AirportService (Coordenadas do Aeroporto)
##    ├── WeatherClient (Dados Meteorológicos - Open-Meteo)
##    ├── CancellationRate (Taxas de Cancelamento Históricas)
##    │
##    └── Features Builder (Engenharia de Features)
##            ↓
##          ML Model (scikit-learn Pipeline)
##            ↓
## [ FastAPI Response ]
##       ↓
## API Java



# Funcionalidades Principais:
Previsão de Atraso de Voo: Retorna "Pontual" ou "Atrasado" com probabilidade.
Geração Dinâmica de Features:
    Features Base: Hora do dia, dia da semana, mês, feriados.
    Features Meteorológicas: Integração com a API Open-Meteo para vento, nuvens, chuva e neve, agregadas por hora.
    Taxas de Cancelamento Históricas: Utiliza dados de CSVs para taxas de cancelamento de companhia aérea, aeroporto de origem e rota nos últimos 30 dias.
Modelo de Machine Learning: Carrega um scikit-learn Pipeline pré-treinado (ColumnTransformer + LogisticRegression).
API Performática: Desenvolvido com FastAPI para alta performance, validação de dados com Pydantic e documentação automática (Swagger UI).
Resiliência e Cache: Utiliza requests-cache para cache de requisições externas e retry-requests para retentar chamadas a APIs em caso de falha.
Assincronicidade: Gerencia chamadas síncronas em ambiente assíncrono com anyio.to_thread.run_sync().

# Tecnologias Utilizadas:
Python 3.x
FastAPI: Framework web assíncrono para construção da API.
Pydantic: Validação de dados (request e response models).
Uvicorn: Servidor ASGI de alta performance.
Pandas: Manipulação de dados e DataFrames.
Scikit-learn: Construção e inferência do modelo de Machine Learning.
Joblib: Serialização e deserialização do modelo de ML.
openmeteo-requests: Cliente Python para a API Open-Meteo.
requests-cache: Cache para requisições HTTP.
retry-requests: Lógica de retry para requisições.
anyio: Biblioteca de E/S assíncrona, usada para executar tarefas síncronas em threads separadas.

# Configuração e Instalação:
Clone o repositório:

git clone https://github.com/AlessandroBentes/fast_flight_api
cd <fast_flight_api>
Crie e ative um ambiente virtual:
python -m venv .venv

No Windows:
.venv\Scripts\activate

No macOS/Linux:
source .venv/bin/activate

# Instale as dependências:
pip install -r requirements.txt
(Crie um requirements.txt com as dependências listadas na seção de tecnologias, incluindo a versão específica do scikit-learn com a qual seu modelo foi treinado, ex: scikit-learn==1.6.1).

# Prepare os arquivos de dados:
Crie a pasta data/ na raiz do projeto.
Adicione os arquivos CSV: airports_lat_lon.csv, ops_airline.csv, ops_origin.csv, ops_route.csv nesta pasta.
Certifique-se de que esses CSVs possuem as colunas esperadas pelos serviços AirportService e CancellationRate.
Prepare o modelo de ML:

# Crie a pasta model/ na raiz do projeto:
Coloque seu modelo treinado (artefato_atraso_voos_rf.joblib) nesta pasta.
IMPORTANTE: Certifique-se de que a versão do scikit-learn instalada no seu ambiente virtual (pip install scikit-learn==X.Y.Z) corresponde exatamente à versão usada para treinar e salvar este arquivo joblib. Caso contrário, ocorrerão erros de deserialização.

# Uso da API:
Inicie o servidor Uvicorn:
uvicorn app.main:app --reload
O servidor estará disponível em http://127.0.0.1:8000.

Acesse a documentação interativa (Swagger UI):
Abra seu navegador e vá para http://127.0.0.1:8000/docs.

Endpoint de Previsão:

POST /api/predict/
Exemplo de Request Body (FlightInput):
{
  "companhia": "AZ",
  "origem": "GIG",
  "destino": "GRU",
  "data_partida": "2025-11-10T14:30:00"
}

Exemplo de Response Body (PredictionOutput):
{
  "previsao": "Pontual",
  "probabilidade": 0.22
}

# Estrutura do Projeto:
### .
### ├── app/
### │   ├── main.py               # Ponto de entrada do FastAPI
### │   ├── routers.py            # Definição do endpoint da API e orquestração dos serviços
### │   ├── schemas.py            # Modelos Pydantic para Request/Response
### │   ├── model.py              # Carregamento e inferência do modelo ML
### │   ├── features.py           # Geração das features base
### │   ├── airport_service.py    # Obtém coordenadas de aeroportos (CSV local)
### │   ├── weather_client.py     # Cliente para API Open-Meteo
### │   ├── weather_features.py   # Agregação de features meteorológicas
### │   └── cancel_rate.py        # Obtenção de taxas de cancelamento históricas
### ├── data/                     # Pasta para arquivos CSV de dados (aeroportos, cancelamentos)
### │   ├── airports_lat_lon.csv
### │   ├── ops_airline.csv
### │   ├── ops_origin.csv
### │   └── ops_route.csv
### ├── model/                    # Pasta para o artefato do modelo ML
### │   └── artefato_atraso_voos_rf.joblib
### ├── .env                      # Variáveis de ambiente (ex: API Keys) - Não incluído no git
### ├── requirements.txt          # Lista de dependências do projeto
### └── README.md                 # Este arquivo


# Desafios Técnicos e Aprendizados:
Integração Assíncrona/Síncrona: A execução de chamadas de API síncronas (openmeteo_requests) dentro de um endpoint async def do FastAPI exigiu o uso de anyio.to_thread.run_sync(). Isso permite que funções bloqueantes sejam executadas em um pool de threads separado, mantendo o loop de eventos principal do FastAPI responsivo.
Versionamento de Modelos ML (joblib): Um desafio significativo foi a incompatibilidade de versões do scikit-learn ao carregar o modelo (InconsistentVersionWarning, AttributeError). A solução crítica foi garantir que a versão do scikit-learn no ambiente de execução da API fosse idêntica à versão utilizada para treinar e serializar o modelo.
Tratamento de Erros Robusto: A implementação de blocos try-except aninhados e o uso de HTTPException garantem que a API forneça respostas de erro claras e informativas ao cliente, enquanto logs detalhados e traceback.format_exc() auxiliam na depuração interna.
Validação de Dados com Pydantic: A utilização de Pydantic para FlightInput e PredictionOutput simplificou a validação de entrada, a serialização/deserialização e a geração automática de documentação da API.
Dockerização: O microserviço e suas dependências foram empacotadas em contêineres Docker para facilitar o deploy e a escalabilidade.

# Melhorias Futuras:
Integração Contínua/Entrega Contínua (CI/CD): Implementar um pipeline para automatizar testes, build e deploy.
Monitoramento: Adicionar ferramentas de monitoramento (ex: Prometheus e Grafana) para observar o desempenho da API e do modelo em produção.
Testes: Desenvolver testes unitários e de integração para todos os módulos e endpoints.
Evolução do Modelo ML: Explorar modelos mais complexos, ensemble methods ou integrar fontes de dados adicionais em tempo real.
Otimização do CancellationRate: Em vez de CSVs, usar um banco de dados ou serviço de cache dedicado para taxas históricas.

Contato:
Para dúvidas ou sugestões, entre em contato:

Alessandro Bentes
alessandro.bentes@gmail.com


