from flask import jsonify

def get_data():
    # Exemplo de dados
    data = {"message": "Dados da API", "values": [1, 2, 3]}
    return jsonify(data)
