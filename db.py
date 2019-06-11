from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


class ForecastDAO():
    """ForecastDAO é responsável pelas interações com o banco de dados"""
    db = SQLAlchemy()
    ma = Marshmallow()
    # Inicializa DB e MA

    def init_db(self, app):
        """Inicia o DB SqlAlchemy"""
        self.db = SQLAlchemy(app)

    def init_ma(self, app):
        """Inicia o serializer Marshmallow"""
        self.ma = Marshmallow(app)

    def create_db(self):
        """Cria o arquivo do banco de dados caso este não exista"""
        if not os.path.isfile('fcast.db'):
            ForecastDAO.db.create_all()
