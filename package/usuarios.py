from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from .auth import token
usuarios_bp = Blueprint('usuarios', __name__)

# Ruta Para Obtener todos los usuarios Registrados en la base de datos 
@usuarios_bp.route("/obtenerUsuarios") 
# @token
def GETusuarios():
    cursor = current_app.mysql.connection.cursor() #Crea Variable para entablar conexion con la base de datos
    cursor.execute("SELECT * FROM t_usuario") #Realizar consulta SQL
    sql = cursor.fetchall()#obtener TODOS los resultados de la consulta
    USUARIOS = []
    for usuario in sql: #Recorrer todos los resutados de la consulta
        USUARIOS.append({ #Creamos tipo Diccinario CLAVE : VALOR
            "usu_id":usuario[0], #La clave tal cual como la tenemos en la base de datos "USU_ID" y el valor seran los indices [Posicion] de recorrer la consulta for ("USUARIO") in sql
            "usu_nombre":usuario[1] ,
            "usu_apellido":usuario[2],
            "usu_telefono":usuario[3], 
            "usu_correo":usuario[4], 
            "usu_tipo_doc":usuario[5], 
            "usu_num_doc":usuario[6], 
            "usu_usuario":usuario[7], 
            "usu_estado":usuario[9], 
            "usu_genero":usuario[10]})
    if len(USUARIOS) < 1:
        return jsonify({"mensaje" : "Ningun Registro Obtenido"}), 404
    return jsonify(USUARIOS), 200

# Ruta Para Registrar un usuario en la base de datos 
@usuarios_bp.route("/registrarUsuario", methods=["POST", "GET"])
# @token
def POSTusuario():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    # Creamos una variable que almacene todas las CLAVE a pedir 
    requerido = ["usu_nombre", #Cada CLAVE como la tenemos en la base de datos, menos el id porque es AI
            "usu_apellido",
            "usu_telefono" ,
            "usu_correo" ,
            "usu_tipo_doc", 
            "usu_num_doc" ,
            "usu_usuario" ,
            "usu_contrasena", 
            "usu_estado", 
            "usu_genero"]
    # creamos una variable con la que podemos exigir a una CLAVE estar en la la Peticion al servidor 
    peticion            = request.json 
    
    # creamos una lista que contiene una estructura de ciclos y condicionales para validar que esten todos los campos en la Peticion
    #             recorre las claves a pedir | verifica si hace falta una clave requerida | verifica si la clave esta en blanco o vacia
    DatosFaltantes = [ x for x in requerido              if x not in peticion                    or not str(peticion[x]).strip()]
    if len(DatosFaltantes)>0: 
        return jsonify({"mensaje": f"Faltan campos en la peticion {DatosFaltantes}"}),400

    nombre              = peticion["usu_nombre"]
    apellido            = peticion["usu_apellido"]
    telefono            = peticion["usu_telefono"]
    correo              = peticion["usu_correo"]
    tipo_doc            = peticion["usu_tipo_doc"]
    num_doc             = peticion["usu_num_doc"]
    usuario             = peticion["usu_usuario"]
    contraseña          = generate_password_hash(peticion["usu_contrasena"])
    estado              = peticion["usu_estado"]
    genero              = peticion["usu_genero"]
    
    #Realizamos Validaciones antes de crear un nuevo registro
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT usu_correo FROM t_usuario WHERE usu_correo = %s", (correo,))
    sql = cursor.fetchone()
    if sql: 
        return jsonify({"mensaje" : "Ya existe un registro asociado con ese correo"}), 409
    
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT usu_num_doc FROM t_usuario WHERE usu_num_doc = %s", (num_doc,))
    sql = cursor.fetchone()
    if sql: 
        return jsonify({"mensaje" : "Ya existe un registro asociado con ese numero de identificacion"}), 409

    if estado.lower() not in ['activo', 'inactivo']:
        return jsonify({"mensaje" : "Esta digitando un valor difente de estado"})
    
    if tipo_doc.lower() not in ['cc', 'ti', 'ce', 'otro']:
        return jsonify({"mensaje" : "Esta digitando un tipo de documento desconocido"})
    
    #si cumple con las validaciones Insertamos el Nuevo Usuario
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("INSERT INTO t_usuario (usu_nombre, usu_apellido, usu_telefono, usu_correo, usu_tipo_doc, usu_num_doc, usu_usuario, usu_contrasena, usu_estado, usu_genero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (nombre, apellido, telefono, correo, tipo_doc, num_doc, usuario, contraseña, estado, genero))
    cursor.connection.commit()
    return jsonify({"mensaje":"Se ha registrado el Usuario"}), 200

#Ruta para Editar un usuario
@usuarios_bp.route("/editarUsuario/<usu_id>", methods=["PUT"])
# @token
def PUTusuario(usu_id):    
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    requerido = ["usu_nombre",
            "usu_apellido",
            "usu_telefono" ,
            "usu_correo" ,
            "usu_tipo_doc", 
            "usu_num_doc" ,
            "usu_usuario" ,
            "usu_contrasena", 
            # "usu_estado", 
            "usu_genero"]
    peticion            = request.json  
    DatosFaltantes = [ x for x in requerido if x not in peticion or not str(peticion[x]).strip()]
    if len(DatosFaltantes)>0:
        return jsonify({"mensaje": f"Faltan campos en la peticion {DatosFaltantes}"}), 400
    nombre              = peticion["usu_nombre"]
    apellido            = peticion["usu_apellido"]
    telefono            = peticion["usu_telefono"]
    correo              = peticion["usu_correo"]
    tipo_doc            = peticion["usu_tipo_doc"]
    num_doc             = peticion["usu_num_doc"]
    usuario             = peticion["usu_usuario"]
    contraseña          = generate_password_hash(peticion["usu_contrasena"])
    # estado              = peticion["usu_estado"]
    genero              = peticion["usu_genero"]
    
    #Realizamos validaciones antes de actualizar el usuario
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (usu_id,))
    sql = cursor.fetchone()
    if not sql: 
        return jsonify({"mensaje" : "Parece que intentas actualizar un registro que NO existe"}), 404
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT usu_correo, usu_id FROM t_usuario WHERE usu_correo = %s AND usu_id != %s", (correo, usu_id,))
    sql = cursor.fetchone()
    if sql: 
        return jsonify({"mensaje" : "No puedes utilizar ese correo porque ya esta asociado a un registro"}), 409
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT usu_num_doc, usu_id FROM t_usuario WHERE usu_num_doc = %s AND usu_id != %s", (num_doc, usu_id,))
    sql = cursor.fetchone()
    if sql: 
        return jsonify({"mensaje" : "No puedes utilizar ese numero de documento porque ya esta asociado a un registro"}), 409

    #Realizamos la actualizacion de los datos del usuario (MENOS DE LOS CAMPOS USU_ESTADO y USU_ID)
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("UPDATE t_usuario SET usu_nombre = %s, usu_apellido=%s, usu_telefono=%s, usu_correo=%s, usu_tipo_doc=%s, usu_num_doc=%s, usu_usuario=%s, usu_contrasena=%s, usu_genero=%s WHERE usu_id = %s", (nombre, apellido, telefono, correo, tipo_doc, num_doc, usuario, contraseña,  genero, usu_id))
    cursor.connection.commit()
    return jsonify({"mensaje":"Se ha editado el Usuario"}), 200

#ruta para cambiar el estado de un usuario
@usuarios_bp.route("/cambiarEstado/<usu_id>", methods=["PUT"]) 
# @token
def PUTestado(usu_id):
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    
    cursor = current_app.mysql.connection.cursor() #hacemos la conexion
    cursor.execute("SELECT usu_id FROM t_usuario WHERE usu_id = %s", (usu_id,)) #realiazamos consulta sql
    sql = cursor.fetchone()#obtenemos un solo resultado
    if not sql: #si no hay resultado de la consulta retorna mensaje
        return jsonify({"mensaje" : "Parece que intentas actualizar el estado de un usuario que no existe"}), 404
    estado = request.json["usu_estado"] #creamos variable estado que contenga requerida la CLAVE "usu_estado" en la peticion
    if estado.lower() not in ['activo', 'inactivo']:
        return jsonify({"mensaje" : "Esta digitando un valor difente de estado"})
    cursor = current_app.mysql.connection.cursor() #hacemos conexion
    cursor.execute("UPDATE t_usuario SET usu_estado=%s WHERE usu_id = %s", (estado, usu_id)) #realizamos consulta sql
    cursor.connection.commit() # no me acuerdo pa que funciona esta
    return jsonify({"mensaje":"Se ha cambiado el estado del usuario"}), 200
