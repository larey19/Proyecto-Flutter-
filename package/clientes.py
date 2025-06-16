from flask import Blueprint, request, jsonify, current_app
from .auth import token
clientes_bp = Blueprint('clientes', __name__)

# Ruta Para Obtener todos los clientes Registrados en la base de datos 
@clientes_bp.route("/obtenerClientes", methods=['GET']) 
@token
def GETclientes():
    cursor = current_app.mysql.connection.cursor() #Crea Variable para entablar conexion con la base de datos
    cursor.execute("SELECT * FROM t_usuario INNER JOIN t_cliente ON usu_id = cli_usu_id") #Realizar consulta SQL
    sql = cursor.fetchall()#obtener TODOS los resultados de la consulta
    CLIENTES = []
    for cliente in sql: #Recorrer todos los resutados de la consulta
        CLIENTES.append({ #Creamos tipo Diccinario CLAVE : VALOR
            "cli_usu_id":cliente[0], #La clave tal cual como la tenemos en la base de datos "cli_usu_id" y el valor seran los indices [Posicion] de recorrer la consulta for ("CLIENTE") in sql
            "usu_nombre":cliente[1] ,
            "usu_apellido":cliente[2],
            "usu_telefono":cliente[3], 
            "usu_correo":cliente[4], 
            "usu_tipo_doc":cliente[5], 
            "usu_num_doc":cliente[6], 
            "usu_usuario":cliente[7], 
            "usu_contraseña":cliente[8], 
            "usu_estado":cliente[9], 
            "usu_genero":cliente[10]})
    if len(CLIENTES) < 1:
        return jsonify({"mensaje" : "Ni un Cliente Obtenido"})
    return jsonify(CLIENTES)

#ruta para Registar un cliente
@clientes_bp.route("/registrarCliente", methods=["POST", "GET"]) 
@token
def POSTcliente():
    if 'cli_usu_id' in request.json:
        cli_usu_id = request.json["cli_usu_id"]
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (cli_usu_id,))
        sql = cursor.fetchone()
        if not sql: 
            return jsonify({"mensaje" : "No existe un usuario registrado con ese ID"}),404
        cursor.execute("SELECT cli_usu_id FROM t_cliente WHERE cli_usu_id = %s", (cli_usu_id,))
        sql = cursor.fetchone()
        if sql: 
            return jsonify({"mensaje" : "Ya existe un Cliente registrado con ese ID"}),409
        
        cursor = current_app.mysql.connection.cursor() #hacemos la conexion
        cursor.execute("INSERT INTO t_cliente (cli_usu_id) SELECT usu_id FROM t_usuario LEFT JOIN t_cliente ON cli_usu_id = usu_id WHERE usu_id = %s", (cli_usu_id,)) #realiazamos consulta sql
        cursor = current_app.mysql.connection.cursor() #hacemos conexion
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha registrado el cliente"}),200
    else:
        return jsonify({"mensaje" : "Debe digitar el ID del usuario que sera cliente"}), 404