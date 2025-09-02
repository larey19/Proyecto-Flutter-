from flask import Blueprint, request, jsonify, current_app
from .auth import token
import uuid
from .smtp import enviar_email
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
            "cli_id":cliente[11], #La clave tal cual como la tenemos en la base de datos "cli_usu_id" y el valor seran los indices [Posicion] de recorrer la consulta for ("CLIENTE") in sql
            "usu_nombre":cliente[1] , 
            "usu_apellido":cliente[2],
            "usu_telefono":cliente[3], 
            "usu_correo":cliente[4], 
            "usu_tipo_doc":cliente[5], 
            "usu_num_doc":cliente[6], 
            "usu_usuario":cliente[7], 
            "usu_estado":cliente[9], 
            "usu_genero":cliente[10]})
    if len(CLIENTES) < 1:
        return jsonify({"mensaje" : "Ni un Cliente Obtenido"})
    return jsonify(CLIENTES)

#ruta para Registar un cliente
@clientes_bp.route("/registrarCliente", methods=["POST", "GET"]) 
@token
def POSTcliente():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if 'usu_num_doc' in request.json:
        cli_id = uuid.uuid4()
        usu_num_doc = request.json["usu_num_doc"]
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT usu_num_doc FROM t_usuario WHERE usu_num_doc = %s", (usu_num_doc,))
        sql = cursor.fetchone()
        if not sql: 
            return jsonify({"mensaje" : "No existe un usuario registrado con ese ID"}),404
        cursor.execute("SELECT cli_id FROM t_usuario JOIN t_cliente ON usu_id = cli_usu_id WHERE usu_num_doc = %s", (usu_num_doc,))
        sql = cursor.fetchone()
        if sql: 
            return jsonify({"mensaje" : "Ya existe un Cliente registrado con ese ID"}),409
        
        cursor.execute("SELECT usu_correo, usu_nombre FROM t_usuario WHERE usu_num_doc = %s", (usu_num_doc,))
        destino = cursor.fetchone()
        enviar_email(destino[0], "Registrado Exitoso", f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');
        * {{
            font-family: 'Montserrat', Arial, Helvetica, sans-serif !important;
        }}
        .email {{
            margin: auto;
            max-width: 500px;
            padding: 5%;
            background-color: rgba(240, 248, 255, 0.377);
        }}
        h4 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #444;
        }}
        h6{{
            margin: 0px auto 15px;
            color : #555;
        }}
        .cont_cent {{
            font-size: 0.9rem;
            line-height: 1.4;
            color : #555;
            text-align: justify
        }}
        .cont_inf {{
            font-size: 0.7rem;
            text-align: center;
            color: #666;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
    </style>
</head>

<body>
    <div class="email">
        <h4>Bienvenido a Barber Blessed 👋</h4>
        <h6>Hola, {destino[0]}</h6>
        <div class="cont_cent">
            <p>{destino[1]} es un placer para nosotros poder darte la bienvenida a nuestra familia, gracias por registrarte en nuestra aplicación móvil.</p>
        </div>
        <hr>
        <div class="cont_inf">  
            <span>Mensaje enviado por <strong>Barber Blessed</strong></span>
        </div>
    </div>
</body>
</html>
""")

        cursor.execute("INSERT INTO t_cliente (cli_id, cli_usu_id) SELECT %s, usu_id FROM t_usuario LEFT JOIN t_cliente ON cli_usu_id = usu_id WHERE usu_num_doc = %s", (cli_id, usu_num_doc,)) #realiazamos consulta sql
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha registrado el cliente"}),200
    else:
        return jsonify({"mensaje" : "Debe digitar el ID del usuario que sera cliente"}), 404
