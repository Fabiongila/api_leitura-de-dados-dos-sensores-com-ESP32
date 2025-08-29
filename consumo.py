from flask import request
from pprint import pprint

resultado_get= request.get_json(
    'https://api-leitura-de-dados-dos-sensores-com.onrender.com'
    '/todos_dados'
)

pprint(resultado_get.json())