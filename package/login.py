from flask import Blueprint, jsonify, request, current_app, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from .smtp import enviar_email
import uuid
import jwt

login_bp = Blueprint('login', __name__)


@login_bp.route("/acceso", methods=["POST"])
def login_flutter():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if 'usu_usuario' in request.json and 'usu_contrasena' in request.json:
        usuario = request.json.get("usu_usuario").strip()
        contrasena = request.json.get("usu_contrasena").strip()
        if not usuario or not contrasena:
            return jsonify({"mensaje": "Para iniciar sesión debes llenar todos los campos"}), 400
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT t_usuario.* FROM t_administrador JOIN t_usuario ON usu_id = adm_usu_id WHERE usu_usuario = %s", (usuario,))
        admin = cursor.fetchone() 
        if not admin:
            cursor.execute("SELECT t_usuario.* FROM t_barbero JOIN t_usuario ON usu_id = bar_usu_id WHERE usu_usuario = %s", (usuario,))
            barber = cursor.fetchone()
            if not barber:
                cursor.execute("SELECT t_usuario.* FROM t_cliente JOIN t_usuario ON usu_id = cli_usu_id WHERE usu_usuario = %s", (usuario,))
                user = cursor.fetchone()
                if not user:
                    return jsonify({"mensaje": "Si no estas registrado, recuerda que puedes hacerlo dando clic en el link aqui abajo!"}), 404
            cursor.close()
        if admin:
            contra_hash = admin[8]
            if not check_password_hash(contra_hash, contrasena):
                return jsonify({"mensaje": "Ups, esa contraseña parece estar incorrecta"}), 404 
            token = jwt.encode({
                'usuario_id': admin[0]
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({
                "mensaje": f"Sesión iniciada con éxito {admin[1]}",
                "token": token, 
                "usu_num_doc": admin[6]
            }), 200
        if barber:
            contra_hash = barber[8]
            if not check_password_hash(contra_hash, contrasena):
                return jsonify({"mensaje": "Ups, esa contraseña parece estar incorrecta"}), 404 
            token = jwt.encode({
                'usuario_id': barber[0]
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({
                "mensaje": f"Sesión iniciada con éxito {barber[1]}",
                "token": token,
                "usu_num_doc": barber[6]
            }), 202
        if user:
            contra_hash = user[8]
            if not check_password_hash(contra_hash, contrasena):
                return jsonify({"mensaje": "Ups, esa contraseña parece estar incorrecta"}), 404 
            token = jwt.encode({
                'usuario_id': user[0]
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({
                "mensaje": f"Sesión iniciada con éxito {user[1]}",
                "token": token,
                "usu_num_doc": user[6]
            }), 201
    return jsonify({"mensaje" : "Error faltan campos en la peticion"}), 404

@login_bp.route("/registro", methods=["POST"])
def registro():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    # Creamos una variable que almacene todas las CLAVE a pedir 
    requerido = [
            "usu_nombre", #Cada CLAVE como la tenemos en la base de datos, menos el id porque es AI
            "usu_apellido",
            "usu_telefono" ,
            "usu_correo" ,
            "usu_tipo_doc", 
            "usu_num_doc" ,
            "usu_usuario" ,
            "usu_contrasena", 
            "usu_genero"]
    # creamos una variable con la que podemos exigir a una CLAVE estar en la la Peticion al servidor 
    peticion            = request.json 
    
    # creamos una lista que contiene una estructura de ciclos y condicionales para validar que esten todos los campos en la Peticion
    #             recorre las claves a pedir | verifica si hace falta una clave requerida | verifica si la clave esta en blanco o vacia
    DatosFaltantes = [ x for x in requerido              if x not in peticion                    or not str(peticion[x]).strip()]
    if len(DatosFaltantes)>0: 
        return jsonify({"mensaje": f"Faltan campos en la peticion {DatosFaltantes}"}),400
    id                  = uuid.uuid4()
    cli_id              = uuid.uuid4()
    nombre              = peticion["usu_nombre"]
    apellido            = peticion["usu_apellido"]
    telefono            = peticion["usu_telefono"]
    correo              = peticion["usu_correo"]
    tipo_doc            = peticion["usu_tipo_doc"]
    num_doc             = peticion["usu_num_doc"]
    usuario             = peticion["usu_usuario"]
    contraseña          = generate_password_hash(peticion["usu_contrasena"])
    genero              = peticion["usu_genero"]
    
    #Realizamos Validaciones antes de crear un nuevo registro
    cursor = current_app.mysql.connection.cursor()    
    cursor.execute("SELECT usu_usuario FROM t_usuario WHERE usu_usuario = %s", (usuario,))
    sql = cursor.fetchone()
    if sql: 
        return jsonify({"mensaje" : "Ya existe un registro con ese usuario"}), 409
    
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

    if tipo_doc.lower() not in ['cc', 'ti', 'ce', 'otro']:
        return jsonify({"mensaje" : "Esta digitando un tipo de documento desconocido"}), 422
    

    #si cumple con las validaciones Insertamos el Nuevo cliente
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("INSERT INTO t_usuario (usu_id ,usu_nombre, usu_apellido, usu_telefono, usu_correo, usu_tipo_doc, usu_num_doc, usu_usuario, usu_contrasena, usu_estado, usu_genero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, nombre, apellido, telefono, correo, tipo_doc, num_doc, usuario, contraseña, "activo", genero))
    
    cursor.execute("SELECT usu_correo, usu_nombre FROM t_usuario WHERE usu_num_doc = %s", (num_doc,))
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
    
    cursor.execute("INSERT INTO t_cliente (cli_id, cli_usu_id) SELECT %s, usu_id FROM t_usuario LEFT JOIN t_cliente ON cli_usu_id = usu_id WHERE usu_num_doc = %s", (cli_id, num_doc,)) 
    cursor.connection.commit()
    return jsonify({"mensaje":"Se ha registrado el cliente"}),200

@login_bp.route("/envioRecuperacion", methods = ["POST"])
def envioRecuperacion():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if "usu_contrasena" in request.json and "usu_num_doc" in request.json:
        usu_num_doc = request.json["usu_num_doc"]
        usu_contrasena = request.json["usu_contrasena"]
        if len(str(usu_contrasena).strip()) == 0 or len(str(usu_num_doc).strip()) == 0:
            return jsonify({"mensaje":"No Puede Ingresar Una Contraseña vacia"}), 400
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT usu_contrasena, usu_num_doc FROM t_usuario WHERE usu_num_doc = %s", (usu_num_doc,))
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"mensaje":"Documento Equivocado"}), 404
        if check_password_hash(usuario[0], usu_contrasena):
            return jsonify({"mensaje": "No Puedes utilizar una Contraseña antigua"}), 404 
        usu_contrasena = generate_password_hash(request.json["usu_contrasena"])
        cursor.execute("UPDATE t_usuario SET usu_contrasena = %s WHERE usu_num_doc = %s", (usu_contrasena, usu_num_doc))
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha cambiado la contraseña correctamente"}), 200
    
    elif "usu_correo" in request.json:
        usu_correo = request.json["usu_correo"]
        if len(str(usu_correo).strip()) == 0:
            return jsonify({"mensaje":"Debe digitar su correo"}), 400
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT usu_num_doc, usu_nombre, usu_apellido FROM t_usuario WHERE usu_correo = %s", (usu_correo,))
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"mensaje":"Parece que ese correo no se encuentra Registrado"}), 404
        enviar_email(usu_correo, "Restablecer Contraseña", f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Recuperar contraseña</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');
    * {{
        font-family: 'Montserrat', Arial, Helvetica, sans-serif !important;
    }}
    body {{
        margin: 0;
        padding: 0;
        background-color: #f4f6f9;
    }}
    .email {{
        margin: auto;
        max-width: 550px;
        padding: 30px;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    h2 {{
        font-size: 1.6rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
    }}
    h6 {{
        margin: 0px auto 15px;
        color: #555;
    }}
    p {{
        font-size: 0.95rem;
        color: #555;
        line-height: 1.5;
    }}
    .btn {{
        display: inline-block;
        padding: 14px 28px;
        background: #1E1E2C;
        color: #ffffff !important;
        text-decoration: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        margin: 25px 0;
    }}
    .cont_inf {{
        font-size: 0.75rem;
        text-align: center;
        color: #777;
        margin-top: 20px;
    }}
    hr {{
        border: none;
        border-top: 1px solid #eee;
        margin: 25px 0;
    }}
</style>
</head>

<body>
<div class="email">
    <h2>Recupera tu contraseña</h2>
    <h6>Hola, {usuario[1]} {usuario[2]}</h6>
    
    <p>
        Hemos recibido una solicitud para restablecer tu contraseña en <strong>Barber Blessed</strong>.
    </p>
    <p>
        Para continuar, haz clic en el siguiente botón. Serás redirigido a la aplicación para establecer tu nueva contraseña.
    </p>

    <a href="https://proyecto-flutter-yt33.onrender.com/recuperacion/{usuario[0]}" class="btn">
        Recuperar contraseña
    </a>

    <p>
        Si no realizaste esta solicitud, puedes ignorar este mensaje. Tu cuenta seguirá segura.
    </p>

    <hr>
    <div class="cont_inf">  
        <span>Mensaje enviado por <strong>Barber Blessed</strong></span>
    </div>
</div>
</body>
</html>
"""
)
        usu = usuario[0]
        return jsonify({"mensaje" : "Siga los pasos Enviados a su Correo"}),200
    else:
        return jsonify({"mensaje" : "Error faltan el correo en la peticion"}), 404
    
@login_bp.route("/recuperacion/<usu_num_doc>")
def recuperar(usu_num_doc):
    return redirect(f"blessedman://recuperar_contrasena?usu_num_doc={usu_num_doc}")
    
