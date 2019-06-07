# Teste técnico Ambar TECH

## Objetivo

Implementar um webservice que utilize um serviço de previsão do tempo (http://apiadvisor.climatempo.com.br/doc/index.html#api-Forecast-Forecast15DaysByCity), e persista os dados no banco de dados relacional (SQLite). 
O backend deve fornecer ainda uma interface
para consumo externo (API RESTful)

# Design
    Aplicação -> API REST -> WebService -> API Previsão do Tempo (Climatempo) -> Database

![Design](/static/img/Design.PNG)

# Regras de negócio

1) O webservice receberá, através de uma interface REST, uma requisição da aplicação com o id de uma cidade como parâmetro;
## Exemplo
    localhost:5000/cidade?id=<ID_DA_CIDADE>


2) O webservice faz uma requisição à API do serviço de previsão do tempo, enviando os parâmetros id e token;

## Exemplo

    http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/<ID_DA_CIDADE>/days/15?token=<TOKEN>

    O token a ser utilizado é o   <u>b22460a8b91ac5f1d48f5b7029891b53</u>



3) Persistir no banco de dados os campos (obtidos na resposta da requisição):

* Nome da cidade
* Estado 
* País 
* Data 
* dados de chuva (probabilidade e precipitação) 
* campos min e max de temperatura.
* A modelagem do banco é de livre escolha do usuário.
4) Implementar uma nova ação que recebe os parâmetros *data_inicial* e *data_final* e, consultando no banco de dados, calcula e retorna
os seguintes valores dentro do período especificado:
## Exemplo
    localhost:5000/analise?data_inicial=<DATA_INICIAL>&data_final=<DATA_FINAL>

* A cidade que possui a maior temperatura máxima.
* Média de precipitação por cidade.
