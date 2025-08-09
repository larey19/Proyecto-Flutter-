from flask import Blueprint, request, jsonify, current_app
from .auth import token
import uuid
reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route("/obtenerReservas")
@token
def GETreserva():
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT * FROM t_reserva")
    sql = cursor.fetchall()
    
    RESERVAS = []
    for res in sql:
        RESERVAS.append({
            "res_id" : res[0],
            "res_fecha" : str(res[1]),
            "res_hora" : str(res[2]),
            "res_descripcion" : res[3],
            "res_serv_id" : res[4],
            "res_bar_id" : res[5],
        })
    if len(sql) < 1:
        return jsonify({"mensaje" : "ningun registro obtenido"}), 404
    print(RESERVAS)
    return jsonify(RESERVAS), 200

@reservas_bp.route("/registrarReserva", methods = ["POST"])
@token
def POSTreserva():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if "res_fecha" in request.json and "res_hora" in request.json and "res_serv_id" in request.json and "res_bar_num_doc" in request.json:
        res_fecha = str(request.json["res_fecha"])
        res_hora  = str(request.json["res_hora"])
        res_serv_id = request.json["res_serv_id"]
        res_descripcion = request.json.get("res_descripcion", "Ninguna")
        res_bar_num_doc  = request.json["res_bar_num_doc"]
        res_id = uuid.uuid4()
        
        if len(str(res_fecha).strip()) < 1 or len((res_hora).strip()) < 1 or len(str(res_serv_id).strip()) < 1 or len(str(res_bar_num_doc).strip()) < 1:
            return jsonify({"mensaje" : "faltan campos por rellenar"}), 400
        
        cursor.execute("SELECT * FROM t_servicio WHERE serv_id = %s", (res_serv_id,))
        if not cursor.fetchone():
            return jsonify({"mensaje": "Uy, parece que no hay ningún servicio con ese ID"}), 404


        cursor.execute("SELECT bar_id FROM t_usuario JOIN t_barbero ON usu_id = bar_usu_id WHERE usu_num_doc = %s", (res_bar_num_doc,))
        if not cursor.fetchone():
            return jsonify({"mensaje": "Uy, parece que no hay ningún barbero con ese ID"}), 404
        
        cursor = current_app.mysql.connection.cursor()
        cursor.execute ("""
                        INSERT INTO t_reserva (res_id, res_fecha, res_hora, res_descripcion , res_serv_id, res_bar_id) 
                        SELECT %s, %s, %s, %s, %s, bar_id FROM t_usuario 
                        JOIN t_barbero ON bar_usu_id = usu_id
                        WHERE usu_num_doc = %s
                        """, (res_id, res_fecha, res_hora, res_descripcion ,res_serv_id, res_bar_num_doc))
        cursor.connection.commit()
        return jsonify({"mensaje":"Se ha realizado la reserva, Se envio la iformacion detallada a su correo"}), 200
    else:
        return jsonify({"mensaje":"Debe enviar toda la informacion solicitada"}), 400