from flask import Flask, g, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

import requests
import datetime
import json
import markdown
import os

TOKEN = 'b22460a8b91ac5f1d48f5b7029891b53'

# Instancia Flask, API, Database e Marshmallow
app = Flask(__name__)
api = Api(app)

# Configurações
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fcast.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)  # DB
ma = Marshmallow(app)  # Marshmallow

# Caso não exista, crio bd.
if not os.path.isfile('fcast.db'):
    db.create_all()


# Models/Classes
class Resposta(db.Model):
    __tablename__ = "resposta"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    rain_prob = db.Column(db.Float, nullable=False)
    rain_prec = db.Column(db.Float, nullable=False)
    min_temp = db.Column(db.Float, nullable=False)
    max_temp = db.Column(db.Float, nullable=False)


class RespostaSchema(ma.ModelSchema):
    class Meta:
        model = Resposta


resposta_schema = RespostaSchema()
respostas_schema = RespostaSchema(many=True)


class ForecastAPI(Resource):
    """ForecastAPI lê o banco de dados"""

    # Códigos de ERRO e mensagens
    erros = {
        1: "Data inicial deve ser menor ou igual que a data final.",
        2: "Data inválida. Datas devem ser passadas no formato AAAA-MM-DD (Dias: entre 01 e 28/30/31 de acordo com o mês. Meses: entre 01 e 12)."
    }

    def date_is_valid(self, date, mask='%Y-%m-%d'):
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

    def get_max_temp(self, filtro_ini, filtro_fim):
        """Retorna maior temperatura máxima dentro do período informado."""
        respostas = db.session.query(
            Resposta.state, Resposta.country, Resposta.city, Resposta.name, db.func.max(
                Resposta.max_temp).label('max_temp')
        ).filter(
            Resposta.date.between(filtro_ini, filtro_fim)).group_by(Resposta.city, Resposta.name, Resposta.state, Resposta.country).first()

        rv = resposta_schema.dump(respostas)
        return rv

    def get_avg_precipitation(self, filtro_ini, filtro_fim):
        """Retorna precipitação e média dados da cidade, dentro do período informado"""
        respostas = db.session.query(
            Resposta.state, Resposta.country, Resposta.city, Resposta.name, db.func.avg(
                Resposta.rain_prec).label('rain_prec')
        ).filter(
            Resposta.date.between(filtro_ini, filtro_fim)).group_by(
                Resposta.city, Resposta.name, Resposta.state, Resposta.country).order_by(Resposta.name)

        rv = respostas_schema.dump(respostas)
        return rv

    def get(self):
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
        max_temp_data = self.get_max_temp(filtro_ini, filtro_fim)
        # Média de precipitação por cidade.
        avg_preci_data = self.get_avg_precipitation(filtro_ini, filtro_fim)

        return {'mensagem': 'Sucesso', 'dados': {'max_temp_data': max_temp_data.data, 'avg_preci_data': avg_preci_data.data}}, 200


class CidadeAPI(Resource):
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

        print(res.status_code)
        if res.status_code == 200:
            return {'mensagem': 'Sucesso', 'dados': res.json()}, res.status_code
        else:
            return {'mensagem': 'Falha', 'dados': []}, res.status_code

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

                for element in data:
                    date_time_obj = datetime.datetime.strptime(
                        element['date'], '%Y-%m-%d')
                    rain_prob = element['rain']['probability']
                    rain_prec = element['rain']['precipitation']
                    max_temp = element['temperature']['max']
                    min_temp = element['temperature']['min']
                    resposta = Resposta(name=name, state=state, city=city, country=country, date=date_time_obj.date(),
                                        rain_prec=rain_prec, rain_prob=rain_prob, max_temp=max_temp, min_temp=min_temp)
                    db.session.add(resposta)

                db.session.commit()
                return {'mensagem': 'Sucesso'}, 201
            else:
                return {'mensagem': 'Falha na requisição'}, res.status_code
        else:
            return {'mensagem': "Argumento inválido, o 'ID' é obrigatório."}, 400


@app.route("/")
def index():
    """Apresenta a documentação do projeto."""
    with open("./README.md", 'r') as markdown_file:
        content = markdown_file.read()
    return markdown.markdown(content)


api.add_resource(ForecastAPI, '/analise/')
api.add_resource(CidadeAPI, '/cidade')
if __name__ == '__main__':
    app.run(debug=True)
