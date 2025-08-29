from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS

# Criar uma API Flask
# Definir a estrutura da tabela sensor
# Definir a estrutura da tabela dados

# Criar uma API Flask
api = Flask(__name__)
CORS(api)

# Criar uma instancia de SQLAlchemy
api.config['SECRET_KEY'] = '12SG860@_R:'
api.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados_sensores.db'

db = SQLAlchemy(api)
db:SQLAlchemy



# Definir a estrutura da tabela dados
# --- id_sensor, nome, dados
class Dispositivo(db.Model):
    _tablename_ = 'dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    #localizacao = db.Column(db.String(100))
    sensores = db.relationship('Sensor', backref='dispositivo', lazy=True)

class Sensor(db.Model):
    _tablename_ = 'sensor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    tipo = db.Column(db.String(50))  # exemplo: temperatura, umidade
    valor = db.Column(db.String)  # último valor lido
   
    dispositivo_id = db.Column(db.Integer, db.ForeignKey('dispositivo.id'))
    
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key =True)
    nome = db.Column(db.String(10))
    email = db.Column(db.String)
    senha = db.Column(db.String(10))
    admin = db.Column(db.Boolean)
    

def inicilizar_banco():
    with api.app_context():
        db.drop_all()
        db.create_all()

        esp32_1= Dispositivo(nome= 'espdrone')
        esp32_2 = Dispositivo(nome='espmaquete')

        usuaurio = Usuario(
            nome = 'Fabio', email = 'fabiongila@gamil.com',
            senha = '12345', admin = True
        )

        db.session.add(esp32_1)
        db.session.add(esp32_2)
        db.session.add(usuaurio)
        db.session.commit()

if __name__ == '__main__':
    inicilizar_banco()

    
