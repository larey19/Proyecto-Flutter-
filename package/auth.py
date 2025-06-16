from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # if 'Authorization' in request.headers:
        #     token = request.headers['Authorization']
        
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(" ")[1]
        if not token:
            return jsonify({"mensaje": "Token requerido"})
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            request.usuario_id = data['usuario_id']
            request.nombre = data.get('nombre')

        except jwt.ExpiredSignatureError:
            return jsonify({"mensaje": "Token expirado"})
        except jwt.InvalidTokenError:
            return jsonify({"mensaje": "Token inválido"})
        return f(*args, **kwargs)
    return decorated
