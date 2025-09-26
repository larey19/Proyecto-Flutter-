from flask import request, jsonify
from dotenv import load_dotenv
from functools import wraps
import jwt
import os 
load_dotenv()

JWT_KEY = os.getenv("JWT_KEY")
def token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None        
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(" ")[1]
        if not token:
            return jsonify({"mensaje": "Token requerido"})
        try:
            data = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
            request.usuario_id = data['usuario_id']
            request.nombre = data.get('nombre')

        except jwt.InvalidTokenError:
            return jsonify({"mensaje": "Token inválido"})
        return f(*args, **kwargs)
    return decorated
