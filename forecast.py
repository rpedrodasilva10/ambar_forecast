from flask import Flask, g
import sqlite3
from flask_sqlalchemy import SQLAlchemy


# Instancia um app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fcast.db'
db = SQLAlchemy(app)

"""
TODO - Criar classe base
Base = db.declarative_base()
class Base(db.Model):
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    nome =  db.Column(db.String(80), unique=True, nullable=False)
"""
#Models
class Pais(db.Model):
    __tablename__ = "pais"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    nome =  db.Column(db.String(80), unique=True, nullable=False)

    
class Estado(db.Model):
    """
    Estados
    """
    __tablename__ = "estado"
    id = db.Column(db.Integer, primary_key=True)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=False)
    
    uf = db.Column(db.String(2),  nullable=False, unique=True)
    # TODO - implementar foreign key
    capital = db.Column(db.String(80), unique=True, nullable=False)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    nome =  db.Column(db.String(80), unique=True, nullable=False)

    

class Cidade(db.Model):
    """
    Cidades
    """
    __tablename__ = "cidade"
    id = db.Column(db.Integer, primary_key=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    nome =  db.Column(db.String(80), unique=True, nullable=False)

   

class Resposta(db.Model):
    __tablename__ = "resposta"
    id = db.Column(db.Integer, primary_key=True)
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidade.id'), nullable=False)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    prob_chuva = db.Column(db.Float, nullable=False)
    preci_chuva = db.Column(db.Float, nullable=False)
    temp_min = db.Column(db.Float, nullable=False)
    temp_max = db.Column(db.Float, nullable=False)

@app.route("/")
def hello():
    return "Hello World!"

