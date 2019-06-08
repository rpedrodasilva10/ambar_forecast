# Teste t&eacute;cnico Ambar Tech

## Objetivo

Implementar um webservice que utilize um servi&ccedil;o de previs&atilde;o do tempo (http://apiadvisor.climatempo.com.br/doc/index.html#api-Forec
ast-Forecast15DaysByCity), e persista os dados no banco de dados relacional (SQLite). 
O backend deve fornecer ainda uma interface
para consumo externo (API RESTful)

# Design
    
Aplica&ccedil;&atilde;o -> API REST -> WebService -> API Previs&atilde;o do Tempo (Climatempo) -> Database

![Design](/static/img/Design.PNG)

# Regras de neg&oacute;cio

1) O webservice receber&aacute;, atrav&eacute;s de uma interface REST, uma requisi&ccedil;&atilde;o da aplica&ccedil;&atilde;o com o id de uma cidade como par&acirc;metro;
## Exemplo
    localhost:5000/cidade?id=<ID_DA_CIDADE>


2) O webservice faz uma requisi&ccedil;&atilde;o &agrave; API do servi&ccedil;o de previs&atilde;o do tempo, enviando os par&acirc;metros id e token;

## Exemplo

    http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/<ID_DA_CIDADE>/days/15?token=<TOKEN>

O token a ser utilizado &eacute; o   b22460a8b91ac5f1d48f5b7029891b53



3) Persistir no banco de dados os campos (obtidos na resposta da requisi&ccedil;&atilde;o):

* Nome da cidade
* Estado 
* Pa&iacute;s 
* Data 
* dados de chuva (probabilidade e precipita&ccedil;&atilde;o) 
* campos min e max de temperatura.
* A modelagem do banco &eacute; de livre escolha do usu&aacute;rio.

4) Implementar uma nova a&ccedil;&atilde;o que recebe os par&acirc;metros *data_inicial* e *data_final* e, consultando no banco de dados, calcula e retorna
os seguintes valores dentro do per&iacute;odo especificado:
## Exemplo
    localhost:5000/analise?data_inicial=<DATA_INICIAL>&data_final=<DATA_FINAL>

* A cidade que possui a maior temperatura m&aacute;xima.
* M&eacute;dia de precipita&ccedil;&atilde;o por cidade.