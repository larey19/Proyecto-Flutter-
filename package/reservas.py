from flask import Blueprint, request, jsonify, current_app
from .auth import token
import uuid
reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route("/obtenerReservas")
@token
def GETreserva():
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("""
                    SELECT 
                        res.res_id, res.res_fecha, res.res_hora , res.res_estado, res.res_descripcion, 
                        serv.serv_id AS res_serv_id, serv.serv_tipo AS res_serv_tipo, serv.serv_precio AS res_serv_precio, 
                        bar.usu_num_doc AS res_bar_num_doc, bar.usu_nombre AS res_bar_nombre, bar.usu_apellido res_bar_apellido,
                        cli.usu_num_doc AS res_cli_num_doc, cli.usu_nombre AS res_cli_nombre, cli.usu_apellido res_cli_apellido 
                    FROM t_reserva res
                    JOIN t_barbero ON bar_id 	        = res_bar_id
                    JOIN t_usuario bar ON bar.usu_id    = bar_usu_id
                    JOIN t_cliente ON cli_id            = cli_usu_id
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
        })
    if len(sql) < 1:
        return jsonify({"mensaje" : "Ninguna reserva obtenida"}), 404
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

        if len(str(res_fecha).strip()) < 1 or len((res_hora).strip()) < 1 or len(str(res_serv_id).strip()) < 1 or len(str(res_bar_num_doc).strip()) < 1 or len(str(res_cli_num_doc).strip()) < 1:
            return jsonify({"mensaje" : "faltan campos por rellenar"}), 400
        
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
                        """, (res_id, res_fecha, res_hora, "pendiente", res_descripcion ,res_serv_id, bar_id, cli_id))
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha realizado la reserva, Se envio la iformacion detallada a su correo"}), 200
    else:
        return jsonify({"mensaje":"Debe enviar toda la informacion solicitada"}), 400
