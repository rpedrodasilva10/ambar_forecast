from db import ForecastDAO


class Resposta(ForecastDAO.db.Model):
    __tablename__ = "resposta"
    id = ForecastDAO.db.Column(ForecastDAO.db.Integer, primary_key=True)
    name = ForecastDAO.db.Column(ForecastDAO.db.String(80), nullable=False)
    state = ForecastDAO.db.Column(ForecastDAO.db.String(80), nullable=False)
    city = ForecastDAO.db.Column(ForecastDAO.db.String(80), nullable=False)
    country = ForecastDAO.db.Column(ForecastDAO.db.String(80), nullable=False)
    date = ForecastDAO.db.Column(ForecastDAO.db.DateTime, nullable=False)
    rain_prob = ForecastDAO.db.Column(ForecastDAO.db.Float, nullable=False)
    rain_prec = ForecastDAO.db.Column(ForecastDAO.db.Float, nullable=False)
    min_temp = ForecastDAO.db.Column(ForecastDAO.db.Float, nullable=False)
    max_temp = ForecastDAO.db.Column(ForecastDAO.db.Float, nullable=False)

    def get_max_temp(self, filtro_ini, filtro_fim):
        """Retorna maior temperatura máxima dentro do período informado."""
        respostas = ForecastDAO.db.session.query(
            Resposta.state, Resposta.country, Resposta.city, Resposta.name, ForecastDAO.db.func.max(
                Resposta.max_temp).label('max_temp')
        ).filter(
            Resposta.date.between(filtro_ini, filtro_fim)).group_by(Resposta.city, Resposta.name, Resposta.state, Resposta.country).first()

        rv = resposta_schema.dump(respostas)
        return rv

    def get_avg_precipitation(self, filtro_ini, filtro_fim):
        """Retorna precipitação e média dados da cidade, dentro do período informado"""
        respostas = ForecastDAO.db.session.query(
            Resposta.state, Resposta.country, Resposta.city, Resposta.name, ForecastDAO.db.func.avg(
                Resposta.rain_prec).label('rain_prec')
        ).filter(
            Resposta.date.between(filtro_ini, filtro_fim)).group_by(
                Resposta.city, Resposta.name, Resposta.state, Resposta.country).order_by(Resposta.name)

        rv = respostas_schema.dump(respostas)
        return rv


class RespostaSchema(ForecastDAO.ma.ModelSchema):
    class Meta:
        model = Resposta


resposta_schema = RespostaSchema()
respostas_schema = RespostaSchema(many=True)
