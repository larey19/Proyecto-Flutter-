from flask import Blueprint, jsonify, request, current_app
import jwt
import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route("/acceso", methods=["POST"])
def login_flutter():
    usuario = request.json.get("usu_usuario").strip()
    contraseña = request.json.get("usu_contraseña").strip()
    if not usuario or not contraseña:
        return jsonify({"mensaje": "Para iniciar sesión debes llenar todos los campos"}), 400
    cursor = current_app.mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM t_usuario WHERE usu_usuario = %s AND usu_contraseña = %s",(usuario, contraseña))
    account = cursor.fetchone()
    cursor.close()
    if account:
        token = jwt.encode({
            'usuario_id': account[0],
            'nombre': account[1],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            "mensaje": f"Sesión iniciada con éxito {account[1]}",
            "token": token
        }), 200
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT * FROM t_usuario WHERE usu_usuario = %s", (usuario,))
    user = cursor.fetchone() 
    if not user:
        return jsonify({"mensaje": "Ups, ese usuario parece estar incorrecto"}), 404
    cursor.execute("SELECT * FROM t_usuario WHERE usu_contraseña = %s", (contraseña,))
    contraseña = cursor.fetchone()
    cursor.close()
    if not contraseña:
        return jsonify({"mensaje": "Ups, esa contraseña parece estar incorrecta"}), 404
    return jsonify({"mensaje": "Credenciales inválidas"}), 400
