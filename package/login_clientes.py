from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import check_password_hash
import jwt

login_clientes_bp = Blueprint('login_clientes', __name__)

@login_clientes_bp.route("/acceso_clientes", methods=["POST"])
def login_flutter():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if 'usu_usuario' in request.json and 'usu_contrasena' in request.json:
        usuario = request.json.get("usu_usuario").strip()
        contraseña = request.json.get("usu_contrasena").strip()
        if not usuario or not contraseña:
            return jsonify({"mensaje": "Para iniciar sesión debes llenar todos los campos"}), 400
        
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM t_usuario JOIN t_cliente ON usu_id = cli_usu_id WHERE usu_usuario = %s", (usuario,))
        user = cursor.fetchone() 
        if not user:
            return jsonify({"mensaje": "Ups, ese usuario parece estar incorrecto. Si eres nuevo puedes registrarte"}), 404
        
        contra_hash = user[8] #el 8 es la posicion de la contraseña de la informacion que esta retornando de usuario
        if not check_password_hash(contra_hash, contraseña):
            return jsonify({"mensaje": "Ups, esa contraseña parece estar incorrecta"}), 404 
        cursor.close()
        if user:
            token = jwt.encode({
                'usuario_id': user[0],
                'nombre': user[1],
                # 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({
                "mensaje": f"Bienvenido {user[1]}",
                "token": token
            }), 200
    return jsonify({"mensaje" : "Error faltan campos en la peticion"}), 404
