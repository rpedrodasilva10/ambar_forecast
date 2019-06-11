from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


class ForecastDAO():
    db = SQLAlchemy()
    ma = Marshmallow()
    # Inicializa DB e MA

    def init_db(self, app):
        self.db = SQLAlchemy(app)

    def init_ma(self, app):
        self.ma = Marshmallow(app)

    def create_db(self):
        if not os.path.isfile('fcast.db'):
            ForecastDAO.db.create_all()
