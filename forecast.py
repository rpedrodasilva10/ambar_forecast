from flask import Flask, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from flask_restplus import Api, Resource

import requests
import datetime
import markdown
import os

from db import ForecastDAO
from models import Resposta, resposta_schema

TOKEN = 'b22460a8b91ac5f1d48f5b7029891b53'

# Instancia Flask, API, Database e Marshmallow
app = Flask(__name__)
api = Api(app)

# Namespace e identificação swagger
ns = api.namespace('', description='Informações sobre previsão do tempo')

# Configurações
app.config.from_pyfile('config.py')
# db = SQLAlchemy(app)  # DB
# ma = Marshmallow(app)  # Marshmallow
ForecastDAO = ForecastDAO()
ForecastDAO.init_db(app)
ForecastDAO.init_ma(app)

# Models/Classes


# Caso não exista, crio bd.
with app.app_context():
    ForecastDAO.create_db()


@ns.route('/analise/')
class ForecastAPI(Resource):
    """ForecastAPI lê o banco de dados"""

    # Códigos de ERRO e mensagens
    erros = {
        1: "Data inicial deve ser menor ou igual que a data final.",
        2: "Data inválida. Datas devem ser passadas no formato AAAA-MM-DD (Dias: entre 01 e 28/30/31 de acordo com o mês. Meses: entre 01 e 12)."
    }

    def date_is_valid(self, date, mask='%Y-%m-%d'):
        """Verifica se a data passada está dentro da máscara passado(mask)"""
        rv = True
        # Inclusão do parâmetro mask para validar dinâmicamente ao formato desejado
        try:
            datetime.datetime.strptime(date, mask)
        except ValueError:
            rv = False
        return rv

    def validate(self, data_inicial, data_final):
        """Checa se as datas recebidas estão dentro do formato (AAAA-MM-DD) e range (inicial <= final) válidos."""
        err_n = 0
        if self.date_is_valid(data_inicial) and self.date_is_valid(data_final):
            if data_inicial > data_final:
                err_n = 1
                return False, err_n
            else:
                return True, err_n
        else:
            err_n = 2
            return False, err_n

    @api.doc(
        responses={
            404: 'Dados não encontrados.',
            200: 'Sucesso.', 400: 'Parâmetro(s) inválido(s).'
        },
        params={
            'data_inicial': 'Data inicial do período (AAAA-MM-DD).', 'data_final': 'Data final do período (AAAA-MM-DD).'
        }
    )
    def get(self):
        """De acordo com as datas passadas, retorna cidade com maior temperatura máxima e média de precipitação por cidade"""
        res = Resposta()  # Instancia resposta para uso dos métodos do modelo
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')

        ok, err_n = self.validate(data_inicial, data_final)
        if ok and err_n == 0:
            filtro_ini = datetime.datetime.strptime(
                data_inicial, '%Y-%m-%d')
            filtro_fim = datetime.datetime.strptime(
                data_final, '%Y-%m-%d')
        else:
            return {'mensagem': self.erros[err_n], 'dados': {"data_inicial": data_inicial, "data_final": data_final}}, 400

        # Cidade com maior temperatura máxima.
        max_temp_data = res.get_max_temp(filtro_ini, filtro_fim)
        # Média de precipitação por cidade.
        avg_preci_data = res.get_avg_precipitation(filtro_ini, filtro_fim)

        return {'mensagem': 'Sucesso', 'dados': {'max_temp_data': max_temp_data.data, 'avg_preci_data': avg_preci_data.data}}, 200


@ns.route("/cidade")
class CidadeAPI(Resource):
    @api.doc(
        responses={
            404: 'Dados não encontrados.',
            200: 'Sucesso.'
        },
        params={
            'name': 'Nome da cidade.',
            'state': 'Sigla do estado.'
        }
    )
    def get(self):
        """Busca as cidades por nome e/ou estado"""
        params = (
            ('name', request.args.get('name', None)),
            ('state', request.args.get('state', None)),
            ('token', TOKEN),
        )
        # API ClimaTempo
        res = requests.get(
            'http://apiadvisor.climatempo.com.br/api/v1/locale/city', params=params)

        if res.status_code == 200:
            return {'mensagem': 'Sucesso', 'dados': res.json()}, res.status_code
        else:
            return {'mensagem': 'Falha', 'dados': []}, res.status_code

    @api.doc(
        responses={
            404: 'Dados não encontrados.',
            201: 'Sucesso. Dados inseridos.',
            400: 'Parâmetro(s) inválido(s).'
        },
        params={
            'id': 'ID da cidade.',
        }
    )
    def post(self):
        """Recebe uma cidade (ID) consome API e persiste informações sobre o clima no banco de dados"""
        params = {'token': TOKEN}
        city_id = str(request.args.get('id', None))

        if not (city_id == 'None'):
            res = requests.get('http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/' +
                               city_id + '/days/15', params=params)
            # Em caso de sucesso na requisição, sigo com a inserção dos itens na base.
            if res.status_code == 200:
                js = res.json()
                name = js['name']
                state = js['state']
                city = js['id']
                country = js['country']
                data = js['data']  # É uma lista

                # Para exibir os objetos inseridos
                objs = []

                for element in data:
                    date_time_obj = datetime.datetime.strptime(
                        element['date'], '%Y-%m-%d')
                    rain_prob = element['rain']['probability']
                    rain_prec = element['rain']['precipitation']
                    max_temp = element['temperature']['max']
                    min_temp = element['temperature']['min']
                    resposta = Resposta(name=name, state=state, city=city, country=country, date=date_time_obj.date(),
                                        rain_prec=rain_prec, rain_prob=rain_prob, max_temp=max_temp, min_temp=min_temp)

                    ForecastDAO.db.session.add(resposta)
                    ForecastDAO.db.session.commit()  # Devo gravar para gerar o ID
                    objs.append(resposta_schema.dump(resposta).data)

                return {'mensagem': 'Sucesso. Dados inseridos', 'dados': objs}, 201
            else:
                return {'mensagem': 'Falha na requisição', 'dados': []}, res.status_code
        else:
            return {'mensagem': "Argumento inválido, o 'ID' é obrigatório.", 'dados': []}, 400


@app.route("/readme")
def get_readme():
    """Apresenta a documentação do projeto."""
    with open("./README.md", 'r') as markdown_file:
        content = markdown_file.read()
    return markdown.markdown(content)


if __name__ == '__main__':
    app.run(debug=True)
