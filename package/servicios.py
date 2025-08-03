from flask import Blueprint, request, jsonify, current_app
from .auth import token
import uuid
servicios_bp = Blueprint("servicios", __name__)

@servicios_bp.route("/obtenerServicios")
@token
def GETservicios():
    cursor = current_app.mysql.connection.cursor() #Crea Variable para entablar conexion con la base de datos
    cursor.execute("SELECT * FROM t_servicio") #Realizar consulta SQL
    sql = cursor.fetchall() #obtener TODOS los resultados de la consulta
    SERVICIOS = []
    for serv in sql: #Recorrer todos los resutados de la consulta
        SERVICIOS.append({ #Creamos tipo Diccinario CLAVE : VALOR
            "serv_id":serv[0], #La clave tal cual como la tenemos en la base de datos "serv_id" y el valor seran los indices [Posicion] de recorrer la consulta for ("SERV") in sql
            "serv_tipo":serv[2] ,
            "serv_precio":serv[1]})
    if len(SERVICIOS) < 1:
        return jsonify({"mensaje" : "Ningun Servicio Obtenido"}), 404
    return jsonify(SERVICIOS), 200

@servicios_bp.route("/registrarServicio", methods=["GET","POST"])
@token
def POSTservicio():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if 'serv_tipo' in request.json and 'serv_precio' in request.json:
        serv_id = uuid.uuid4()
        serv_tipo = request.json["serv_tipo"]
        serv_precio = request.json["serv_precio"]
        if len(str(serv_tipo).strip()) < 1 or len(str(serv_precio).strip()) < 1: 
            return jsonify({"mensaje":"Faltan campos por rellenar"}), 400
        cursor = current_app.mysql.connection.cursor() #Crea Variable para entablar conexion con la base de datos
        cursor.execute("INSERT INTO t_servicio (serv_id, serv_tipo, serv_precio) VALUES (%s, %s, %s)", (serv_id, serv_tipo, serv_precio,)) #Realizar consulta SQL
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha registrado el Servicio"}), 200
    else:
        return jsonify({"mensaje":"Debe digitar el Tipo de Servicio y el Precio de este mismo!"}), 400

@servicios_bp.route("/editarServicio/<serv_id>", methods=["PUT"])
@token
def PUTservicio(serv_id):
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if 'serv_tipo' in request.json and 'serv_precio' in request.json:
        serv_tipo = request.json["serv_tipo"]
        serv_precio = request.json["serv_precio"]
        if len(str(serv_tipo).strip()) < 1 or len(str(serv_precio).strip()) < 1: 
            return jsonify({"mensaje":"Faltan campos por rellenar"}), 400
        cursor = current_app.mysql.connection.cursor() #Crea Variable para entablar conexion con la base de datos
        cursor.execute("UPDATE t_servicio SET serv_tipo = %s,  serv_precio = %s WHERE serv_id = %s", (serv_tipo, serv_precio, serv_id,)) #Realizar consulta SQL
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha Editado el Servicio"}), 200
    else:
        return jsonify({"mensaje":"Debe digitar el Tipo de Servicio y el Precio de este mismo!"}), 400
