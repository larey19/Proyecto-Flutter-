from flask import Blueprint, request, jsonify, current_app
from .auth import token
barberos_bp = Blueprint('barberos', __name__)

# Ruta Para Obtener todos los barberos Registrados en la base de datos 
@barberos_bp.route("/obtenerBarberos") 
@token
def GETbarberos():
    cursor = current_app.mysql.connection.cursor() #Crea Variable para entablar conexion con la base de datos
    cursor.execute("SELECT * FROM t_usuario INNER JOIN t_barbero ON usu_id = bar_usu_id") #Realizar consulta SQL
    sql = cursor.fetchall() #obtener TODOS los resultados de la consulta
    BARBEROS = []
    for barbero in sql: #Recorrer todos los resutados de la consulta
        BARBEROS.append({ #Creamos tipo Diccinario CLAVE : VALOR
            "bar_id":barbero[11], #La clave tal cual como la tenemos en la base de datos "bar_usu_id" y el valor seran los indices [Posicion] de recorrer la consulta for ("barberos") in sql
            "usu_nombre":barbero[1] ,
            "usu_apellido":barbero[2], 
            "usu_telefono":barbero[3], 
            "usu_correo":barbero[4], 
            "usu_tipo_doc":barbero[5], 
            "usu_num_doc":barbero[6], 
            "usu_usuario":barbero[7], 
            "usu_estado":barbero[9], 
            "usu_genero":barbero[10],
            "bar_salario": barbero[12],
            })
    if len(BARBEROS) < 1:
        return jsonify({"mensaje" : "Ningun barbero Obtenido"}), 404
    return jsonify(BARBEROS), 200

#ruta para Registar un Barbero
@barberos_bp.route("/registrarBarbero", methods=["POST", "GET"]) 
@token
def POSTbarberos():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if 'bar_salario' in request.json and 'usu_num_doc' in request.json:
        usu_num_doc = request.json["usu_num_doc"]
        bar_salario = request.json["bar_salario"]
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT usu_num_doc FROM t_usuario WHERE usu_num_doc = %s", (usu_num_doc,))
        sql = cursor.fetchone()
        if not sql: 
            return jsonify({"mensaje" : "No existe un usuario registrado con ese ID"}),404
        cursor.execute("SELECT bar_id FROM t_usuario JOIN t_barbero ON usu_id = bar_usu_id WHERE usu_num_doc = %s", (usu_num_doc,))
        sql = cursor.fetchone()
        if sql: 
            return jsonify({"mensaje" : "Ya existe un barbero registrado con ese ID"}),409
        cursor = current_app.mysql.connection.cursor() #hacemos la conexion
        cursor.execute("INSERT INTO t_barbero (bar_salario, bar_usu_id) SELECT %s, usu_id FROM t_usuario LEFT JOIN t_barbero ON usu_num_doc = usu_id WHERE usu_num_doc = %s", (bar_salario, usu_num_doc,)) #realiazamos consulta sql
        cursor = current_app.mysql.connection.cursor() #hacemos conexion
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha registrado el barbero"}),200
    else:
        return jsonify({"mensaje" : "Debe digitar el Salario e ID del usuario que sera barbero"}), 400
