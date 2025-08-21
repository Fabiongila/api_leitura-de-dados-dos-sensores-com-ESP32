from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Dispositivo, Sensor, Usuario, api, db
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
import os


def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token= request.headers['x-access-token']
        if not token:
            return jsonify({'Mensagem': 'Token não foi incluído'}, 401)
        # Se temos um token, validar o acesso ao db
        try:
            resultado = jwt.decode(token, api.config['SECRET_KEY'], algorithms=["HS256"])
            print(resultado)
            usuario = Usuario.query.filter_by(id_usuario=resultado['id_usuario']).first()
        except Exception:
            print(Exception)
            return jsonify({'Mensagem': 'Token é inválido'}, 401)
        return f(usuario, *args, **kwargs)
    return decorated


@api.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401,  {'WWW-Authenticate': 'Basic realm ="Login obrigatório"'})
    usuário = Usuario.query.filter_by(nome= auth.username).first()
    if not usuário:
         return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm ="Login obrigatório"'})
    if auth.password == usuário.senha:
        global token
        token = jwt.encode({'id_usuario': usuário.id_usuario, 'exp':datetime.now(timezone.utc) + timedelta(minutes=30)}, api.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
        
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm ="Login obrigatório"'})

   
# Todos os dados
@api.route('/todos_dados', methods=['GET'])
def obter_dados():
    dados = Dispositivo.query.all()


    lista_dados = []
    for dado in dados:
        dados_atual = {}
        dados_atual['id_dispositivo'] = dado.id
        dados_atual['nome'] = dado.nome
        dados_atual['sensores'] = dado.sensores
        lista_dados.append(dados_atual)

    return jsonify({'Dados': lista_dados})

# Dados de cada ESP32
@api.route('/dispositivo/<string:nome>', methods = ['GET'])
def obter_dados_por_id(nome):
    dispisitivo = Dispositivo.query.filter_by(nome=nome).first_or_404()
    sensores_agrupados = []
    for sensor in dispisitivo.sensores:
        sensores_agrupados.append(
            {'sensor_id': sensor.id
             },
             {'valor': sensor.valor
              }
        )
    return jsonify(
        {'Dispositivo': dispisitivo.nome,
         'Sensores': sensores_agrupados
         }
    )


# Todos sensores
@api.route('/sensores', methods=['GET'])
def todos_sensores():
    sensores = Sensor.query.all()
    resultado = []
    for sensor in sensores:
        resultado.append({
            'Sensor_id': sensor.id,
            'Nome_sensor': sensor.nome,
            'Valor': sensor.valor,
            'Dispositivo_id': sensor.dispositivo_id
        })
    return jsonify(resultado)

# Dados de sensor específico
@api.route('/dispositivo/<string:nome>/<string:tipo>', methods=['GET'])
def sensor(nome, tipo):
    dispositivo = Dispositivo.query.filter_by(nome=nome).first()
    if not dispositivo:
        return jsonify({'EErro': 'Dispositivo não encontrado'}, 404)
    sensor = Sensor.query.filter_by(tipo =tipo, id=dispositivo.id).first()
    if not sensor:
        return jsonify({'Erro': 'Sensor nao encontrado'}, 404)
    return jsonify({
        'Sensor': sensor.tipo,
        'Valor': sensor.valor
    })


# Rota pra ESP32 enviar dados para a API:
@api.route('/dados', methods= ['POST'])
def recebe_dados():
    dados= request.get_json()
    dispositivo_nome = dados.get('dispositvo_nome')
    sensores = dados.get('sensores')
   
    dispositivo= Dispositivo.query.filter_by(nome=dispositivo_nome).first()
    if not dispositivo or not sensores:
        return jsonify({'Erro': 'Dados incompletos'}, 400 )
    
    for dados_sensor in sensores:
        tipo = dados_sensor.get('tipo')
        valor = dados_sensor.get('valor')

        sensor = Sensor(
            tipo = tipo,
            valor = valor,
            dispositivo_id = dispositivo.id
        )
        db.session.add(sensor)
        db.session.commit()

         
if __name__ == '__main__':
    from os import environ
    api.run(host='0.0.0.0', port=int(environ.get('PORT', 5000)))