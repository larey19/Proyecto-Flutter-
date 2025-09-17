from flask import Blueprint, request, jsonify, current_app
from .auth import token
import uuid
from .smtp import enviar_email
from datetime import datetime

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route("/obtenerReservas")
@token
def GETreserva():
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("""
                    SELECT 
                        res.res_id, res.res_fecha, res.res_hora , res.res_estado, res.res_descripcion, 
                        serv.serv_id AS res_serv_id, serv.serv_tipo AS res_serv_tipo, serv.serv_precio AS res_serv_precio, 
                        bar.usu_num_doc AS res_bar_num_doc, bar.usu_nombre AS res_bar_nombre, bar.usu_apellido AS res_bar_apellido,
                        cli.usu_num_doc AS res_cli_num_doc, cli.usu_nombre AS res_cli_nombre, cli.usu_apellido AS res_cli_apellido, cli.usu_telefono AS res_cli_telefono 
                    FROM t_reserva res
                        JOIN t_barbero ON bar_id 	        = res_bar_id
                        JOIN t_usuario bar ON bar.usu_id    = bar_usu_id
                        JOIN t_cliente ON cli_id            = res_cli_id
                        JOIN t_usuario cli ON cli.usu_id    = cli_usu_id
                        JOIN t_servicio serv ON serv_id     = res_serv_id
                    """)
    sql = cursor.fetchall()
    RESERVAS = []
    for res in sql:
        RESERVAS.append({
            "res_id" : res[0],
            "res_fecha" : str(res[1]),
            "res_hora" : str(res[2]),
            "res_estado" : res[3],
            "res_descripcion" : res[4],
            "res_serv_id" : res[5],
            "res_serv_tipo": res[6],
            "res_serv_precio": res[7],
            "res_bar_num_doc": res[8],
            "res_bar_nombre" : res[9],
            "res_bar_apellido" : res[10],
            "res_cli_num_doc": res[11],
            "res_cli_nombre" : res[12],
            "res_cli_apellido" : res[13],
            "res_cli_telefono" : res[14]
        })
    if len(sql) < 1:
        return jsonify({"mensaje" : "Ninguna reserva obtenida"}), 404
    return jsonify(RESERVAS), 200

@reservas_bp.route("/obtenerReservas/<res_num_doc>")
@token
def GETreservasUsuario(res_num_doc):
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT * FROM t_barbero JOIN t_usuario ON usu_id = bar_usu_id WHERE t_usuario.usu_num_doc = %s", (res_num_doc,))
    bar_num = cursor.fetchone()
    if not bar_num:
        cursor.execute("SELECT * FROM t_cliente JOIN t_usuario ON usu_id = cli_usu_id WHERE t_usuario.usu_num_doc = %s", (res_num_doc,))
        cli_num = cursor.fetchone()
        if not cli_num:
            return jsonify({"mensaje" : "Parece que ese usuario No existe"}), 404
    cursor.execute("""
                    SELECT 
                        res.res_id, res.res_fecha, res.res_hora , res.res_estado, res.res_descripcion, 
                        serv.serv_id AS res_serv_id, serv.serv_tipo AS res_serv_tipo, serv.serv_precio AS res_serv_precio, 
                        bar.usu_num_doc AS res_bar_num_doc, bar.usu_nombre AS res_bar_nombre, bar.usu_apellido AS res_bar_apellido,
                        cli.usu_num_doc AS res_cli_num_doc, cli.usu_nombre AS res_cli_nombre, cli.usu_apellido AS res_cli_apellido, cli.usu_telefono AS res_cli_telefono 
                    FROM t_reserva res
                        JOIN t_barbero ON bar_id 	        = res_bar_id
                        JOIN t_usuario bar ON bar.usu_id    = bar_usu_id
                        JOIN t_cliente ON cli_id            = res_cli_id
                        JOIN t_usuario cli ON cli.usu_id    = cli_usu_id
                        JOIN t_servicio serv ON serv_id     = res_serv_id
                    WHERE bar.usu_num_doc = %s or cli.usu_num_doc = %s
                    """, (res_num_doc, res_num_doc,))
    sql = cursor.fetchall()
    RESERVAS = []
    for res in sql:
        RESERVAS.append({
            "res_id" : res[0],
            "res_fecha" : str(res[1]),
            "res_hora" : str(res[2]),
            "res_estado" : res[3],
            "res_descripcion" : res[4],
            "res_serv_id" : res[5],
            "res_serv_tipo": res[6],
            "res_serv_precio": res[7],
            "res_bar_num_doc": res[8],
            "res_bar_nombre" : res[9],
            "res_bar_apellido" : res[10],
            "res_cli_num_doc": res[11],
            "res_cli_nombre" : res[12],
            "res_cli_apellido" : res[13],
            "res_cli_telefono" : res[14]
        })
    if len(sql) < 1:
        return jsonify({"mensaje" : "Aun no has realizado ninguna reserva?\n La puedes realizar ya mismo!"}), 404
    return jsonify(RESERVAS), 200

@reservas_bp.route("/registrarReserva", methods = ["POST"])
@token
def POSTreserva():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if "res_fecha" in request.json and "res_hora" in request.json and "res_serv_id" in request.json and "res_bar_num_doc" in request.json and "res_cli_num_doc" in request.json:
        res_fecha = str(request.json["res_fecha"])
        res_hora  = str(request.json["res_hora"])
        res_serv_id = request.json["res_serv_id"]
        res_descripcion = request.json.get("res_descripcion", "Ninguna")
        res_bar_num_doc  = request.json["res_bar_num_doc"]
        res_cli_num_doc  = request.json["res_cli_num_doc"]
        res_id = uuid.uuid4()
        time = datetime.now().strftime("%Y-%m-%d %H:%M")
        if len(str(res_fecha).strip()) < 1 or len((res_hora).strip()) < 1 or len(str(res_serv_id).strip()) < 1 or len(str(res_bar_num_doc).strip()) < 1 or len(str(res_cli_num_doc).strip()) < 1:
            return jsonify({"mensaje" : "faltan campos por rellenar"}), 400
        
        if len(str(res_descripcion).strip()) == 0:
            res_descripcion = "Ninguna"

        try: 
            fch = datetime.strptime(f"{res_fecha} {res_hora}", "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return jsonify({"mensaje": "Formato de fecha equivocado"}), 422 

        if time >= fch:
            return jsonify({"mensaje": f"No puede digitar una fecha Antigua {time} {fch}"}), 422 

        cursor = current_app.mysql.connection.cursor()       
        cursor.execute("SELECT * FROM t_servicio WHERE serv_id = %s", (res_serv_id,))
        if not cursor.fetchone():
            return jsonify({"mensaje": "Uy, parece que no hay ningún servicio con ese ID"}), 404

        cursor.execute("SELECT cli_id FROM t_usuario JOIN t_cliente ON usu_id = cli_usu_id WHERE usu_num_doc = %s", (res_cli_num_doc,))
        cli_id = cursor.fetchone()
        if not cli_id:
            return jsonify({"mensaje": "Uy, parece que no hay ningún cliente con ese ID"}), 404

        cursor.execute("SELECT bar_id FROM t_usuario JOIN t_barbero ON usu_id = bar_usu_id WHERE usu_num_doc = %s", (res_bar_num_doc,))
        bar_id = cursor.fetchone()
        if not bar_id:
            return jsonify({"mensaje": "Uy, parece que no hay ningún barbero con ese ID"}), 404
        
        cursor.execute ("""
                        INSERT INTO t_reserva (res_id, res_fecha, res_hora, res_estado, res_descripcion , res_serv_id, res_bar_id, res_cli_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (res_id, res_fecha, res_hora, "Confirmada", res_descripcion ,res_serv_id, bar_id, cli_id))
        cursor.connection.commit()
        cursor.execute("""
                    SELECT 
                        res.res_id, res.res_fecha, res.res_hora , res.res_estado, res.res_descripcion, 
                        serv.serv_id AS res_serv_id, serv.serv_tipo AS res_serv_tipo, serv.serv_precio AS res_serv_precio, 
                        bar.usu_num_doc AS res_bar_num_doc, bar.usu_nombre AS res_bar_nombre, bar.usu_apellido AS res_bar_apellido,
                        cli.usu_num_doc AS res_cli_num_doc, cli.usu_nombre AS res_cli_nombre, cli.usu_apellido AS res_cli_apellido, cli.usu_correo
                        FROM t_reserva res
                        JOIN t_barbero ON bar_id 	        = res_bar_id
                        JOIN t_usuario bar ON bar.usu_id    = bar_usu_id
                        JOIN t_cliente ON cli_id            = res_cli_id
                        JOIN t_usuario cli ON cli.usu_id    = cli_usu_id
                        JOIN t_servicio serv ON serv_id     = res_serv_id
                    WHERE res_cli_id = %s
                    """, (cli_id))
        res = cursor.fetchone()
        enviar_email(res[14], "Reserva Confirmada!" ,f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reserva Confirmada</title>
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
            max-width: 600px;
            padding: 30px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h4{{
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}
        h6 {{
            margin: 0 0 15px;
            color: #444;
        }}
        p {{
            color: #555;
            font-size: 0.8rem;
        }}
        .info {{
            background: #f9fafc;
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }}
        .item{{
            margin-bottom: 8px;
            font-size: 0.9rem;
        }}
        .cont_inf {{
            text-align: center;
            font-size: 0.75rem;
            color: #666;
            margin-top: 25px;
        }}
    </style>
</head>

<body>
    <div class="email">
        <h4>¡Tu reserva está confirmada!</h4>
        <h6>Hola, {res[12]} {res[13]}</h6>
        <p>
            {res[12]} Aquí tienes el resumen de tu reserva:
        </p>
        <div class="info">
            <div class="item"><strong>Estado: </strong> {res[3]}</div>
            <div class="item"><strong>Fecha:</strong> {res[1]} </div>
            <div class="item"><strong>Hora:</strong> {res[2]} </div>
            <div class="item"><strong>Descripción:</strong> {res[4]} </div>
        </div>

        <div class="info">
            <div class="item"><strong>Barbero:</strong> {res[9]} {res[10]} </div>
        </div>

        <div class="info">
            <div class="item"><strong>Servicio:</strong> {res[6]} </div>
            <div class="item"><strong>Precio:</strong> ${res[7]} </div>
        </div>

        <div class="cont_inf">  
            <span>Mensaje enviado por <strong>Barber Blessed</strong></span>
        </div>
    </div>
</body>
</html>
""")
        return jsonify({"mensaje":"Se ha realizado la reserva, Se envio la iformacion detallada a su correo"}), 200
    else:
        return jsonify({"mensaje":"Debe enviar toda la informacion solicitada"}), 400

@reservas_bp.route("/editarReserva/<res_id>", methods = ["PUT"])
@token
def PUTreserva(res_id):
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if "res_fecha" in request.json and "res_hora" in request.json:
        res_fecha = str(request.json["res_fecha"])
        res_hora  = str(request.json["res_hora"])
        res_descripcion = request.json.get("res_descripcion", "Ninguna")

        time = datetime.now()
        if len(str(res_id).strip()) < 1 or len(str(res_fecha).strip()) < 1 or len((res_hora).strip()) < 1:
            return jsonify({"mensaje" : "faltan campos por rellenar"}), 400
        
        if len(str(res_descripcion).strip()) == 0:
            res_descripcion = "Ninguna"

        cursor = current_app.mysql.connection.cursor()    
        cursor.execute("SELECT * FROM t_reserva WHERE res_id = %s", (res_id,))
        reserva = cursor.fetchone()
        if not reserva:
            return jsonify({"mensaje" : "Uy, parece que no hay ninguna reserva con ese ID"}), 404
        
        cursor.execute("SELECT res_estado FROM t_reserva WHERE res_id = %s", (res_id,))
        reserva = cursor.fetchone()
        if reserva[0].lower() == "completada" or reserva[0].lower() == "cancelada":
            return jsonify({"mensaje" : "¡No se puede Reprogramar esta Reserva porque su estado no lo permite!"}), 401
        try: 
            fch = datetime.strptime(f"{res_fecha} {res_hora}", "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"mensaje": f"Formato de fecha equivocado, {fch} - {time}"}), 422 

        if time >= fch:
            return jsonify({"mensaje": "No puede digitar una fecha Antigua"}), 422 
        
        cursor.execute ("""
                        UPDATE t_reserva SET res_fecha = %s, res_hora = %s, res_estado = %s, res_descripcion  = %s WHERE res_id = %s 
                        """, (res_fecha, res_hora, "Reprogramada", res_descripcion, res_id))
        cursor.connection.commit()
        cursor.execute("""
                    SELECT 
                        serv.serv_tipo,
                        cli.usu_nombre, cli.usu_apellido, cli.usu_correo,
                        res.res_fecha, res.res_hora
                        FROM t_reserva res
                        JOIN t_cliente ON cli_id            = res_cli_id
                        JOIN t_usuario cli ON cli.usu_id    = cli_usu_id
                        JOIN t_servicio serv ON serv_id     = res_serv_id
                    WHERE res_id = %s
                    """, (res_id,))
        res = cursor.fetchone()
        enviar_email(res[3], "Reprogramaste tu reserva!", f"""
<!DOCTYPE html>
<html lang="es">
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
        h6 {{
            margin: 0px auto 15px;
            color: #555;
        }}
        .cont_cent {{
            font-size: 0.9rem;
            line-height: 1.4;
            color: #555;
            text-align: justify;
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
        <h4>¡Tu reserva ha sido reprogramada correctamente!</h4>
        <h6>Hola, {res[1]} {res[2]} 👋</h6>
        <div class="cont_cent">
            <p>
                Te confirmamos que tu reserva del servicio <strong>{res[0]}</strong> 
                ha sido actualizada exitosamente.
            </p>
            <p>
                La nueva fecha y hora de tu cita es el <strong>{res[4]}</strong> a las <strong>{res[5]}</strong>.
            </p>
            <p>
                ¡Gracias por confiar en nosotros! Te estaremos esperando con mucho gusto.
            </p>
        </div>
        <hr>
        <div class="cont_inf">  
            <span>Mensaje enviado por <strong>Barber Blessed</strong></span>
        </div>
    </div>
</body>
</html>
""")
        return jsonify({"mensaje":"Se ha Reprogramado la reserva con exito, Revise la bandeja de su correo"}), 200
    else:
        return jsonify({"mensaje":"Debe enviar toda la informacion solicitada"}), 400

@reservas_bp.route("/editarEstado/<res_id>", methods = ["PUT"])
@token
def PUTreservaestado(res_id):
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if "res_estado" in request.json:
        dtll_id = uuid.uuid4()
        res_estado = request.json["res_estado"]
        cursor = current_app.mysql.connection.cursor() 
        cursor.execute("SELECT res_estado, res_serv_id, res_bar_id, res_cli_id FROM t_reserva WHERE res_id = %s", (res_id,))
        reserva = cursor.fetchone()
        if not reserva:
            return jsonify({"mensaje" : "Uy, parece que no hay ninguna reserva con ese ID"}), 404
        if len(str(res_estado).strip()) == 0:
            return jsonify({"mensaje" : "Debe seleccionar un estado"}), 400
        if res_estado.lower() not in ["confirmada", "cancelada", "completada", "reprogramada"]:
            return jsonify({"mensaje":"Esta digitando un valor de estado no admitido"}), 422
        if reserva[0].lower() == "reprogramada":
            return jsonify({"mensaje" : "Para reprogramar tu reserva correctamente, debes editarla por completo"}), 401
        if reserva[0].lower() == "completada" or reserva[0].lower() == "cancelada":
            return jsonify({"mensaje" : "¡No se puede Reprogramar esta Reserva porque su estado no lo permite!"}), 401
        if reserva[0].lower() == res_estado.lower():
            return jsonify({"mensaje":"Esta Seleccionando el estado actual de la reserva"}), 409
        res_estado = res_estado.capitalize()
        cursor.execute("UPDATE t_reserva SET res_estado = %s WHERE res_id = %s ", (res_estado ,res_id))
        cursor.connection.commit()
        cursor.execute("""
                    SELECT 
                        serv.serv_tipo,
                        cli.usu_nombre, cli.usu_apellido, cli.usu_correo,
                        res.res_fecha, res.res_hora
                        FROM t_reserva res
                        JOIN t_cliente ON cli_id            = res_cli_id
                        JOIN t_usuario cli ON cli.usu_id    = cli_usu_id
                        JOIN t_servicio serv ON serv_id     = res_serv_id
                    WHERE res_id = %s
                    """, (res_id,))
        res = cursor.fetchone()
        if res_estado == "Completada":
            cursor.execute("INSERT INTO t_dtll_serv (dtll_id, dtll_serv_id, dtll_cli_id, dtll_bar_id) VALUES (%s, %s, %s, %s)", (dtll_id, reserva[1], reserva[3], reserva[2],))
            cursor.connection.commit()
            return jsonify({"mensaje": "La reserva se ha Completado con exito y se ha registrado toda la informacion en los detalles de servicios."}), 200
        if res_estado == "Cancelada":
            enviar_email(res[3], "Acabas de cancelar tu reserva", f"""
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
        <h4>Acabas de cancelar tu reserva!</h4>
        <h6>Hola, {res[1]} {res[2]} 👋</h6>
        <div class="cont_cent">
            <p>{res[1]}, tu reserva del servicio {res[0]} para el dia {res[4]} ha sido cancelada exitosamente.  
            </p>
            <p>
                Si lo deseas, puedes programar una nueva cita en cualquier momento desde nuestra aplicación.  
                ¡Siempre será un placer atenderte!
            </p>
        </div>
        <hr>
        <div class="cont_inf">  
            <span>Mensaje enviado por <strong>Barber Blessed</strong></span>
        </div>
    </div>
</body>
</html>
""")
        return jsonify({"mensaje":"El estado se ha actualizado correctamente"})
    else:
        return jsonify({"mensaje":"Faltan campos en la peticion"})


