from flask import Blueprint, request, jsonify, current_app
from .auth import token
detal_servicios_bp = Blueprint("detal_servicios", __name__)

@detal_servicios_bp.route("/obtenerDetalleServicios")
@token
def GETservicios():
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("""
                    SELECT 
                        dtll_id,
                        serv.serv_tipo, serv.serv_precio, serv_id AS dtll_serv_id,
                        u_cli.usu_nombre AS cli_nombre, u_cli.usu_apellido AS cli_apellido, u_cli.usu_num_doc AS dtll_cli_num_doc,
                        u_bar.usu_nombre AS bar_nombre, u_bar.usu_apellido AS bar_apellido, u_bar.usu_num_doc AS dtll_bar_num_doc
                    FROM t_dtll_serv detalle
                    INNER JOIN t_servicio serv ON detalle.dtll_serv_id = serv.serv_id
                    INNER JOIN t_cliente cli ON detalle.dtll_cli_id = cli.cli_id
                    INNER JOIN t_usuario u_cli ON cli.cli_usu_id = u_cli.usu_id
                    INNER JOIN t_barbero bar ON detalle.dtll_bar_id = bar.bar_id
                    INNER JOIN t_usuario u_bar ON bar.bar_usu_id = u_bar.usu_id;
                    """)
    sql = cursor.fetchall()
    DTL_SERVICIOS = []
    for serv in sql:
        DTL_SERVICIOS.append({
            "dtll_id":      serv[0],
            "serv_tipo":    serv[1],
            "serv_precio":  serv[2],
            "dtll_serv_id":  serv[3],
            "cli_nombre":   serv[4],
            "cli_apellido": serv[5],
            "dtll_cli_num_doc": serv[6],
            "bar_nombre":   serv[7],
            "bar_apellido": serv[8],
            "dtll_bar_num_doc": serv[9]
        })

    if len(DTL_SERVICIOS) < 1:
        return jsonify({"mensaje": "Ningún Detalle de Servicio Obtenido"}), 404
    return jsonify(DTL_SERVICIOS), 200

@detal_servicios_bp.route("/registrarDetalleServicio", methods=["GET", "POST"])
@token
def POSTdetalServicio():
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    
    if 'dtll_serv_id' in request.json and 'dtll_cli_num_doc' in request.json and 'dtll_bar_num_doc' in request.json:
        dtll_serv_id = request.json["dtll_serv_id"]
        dtll_cli_num_doc = request.json["dtll_cli_num_doc"]
        dtll_bar_num_doc = request.json["dtll_bar_num_doc"]
        
        if not all([dtll_serv_id, dtll_cli_num_doc, dtll_bar_num_doc]): 
            return jsonify({"mensaje": "Faltan campos por rellenar"}), 400
        
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM t_servicio WHERE serv_id = %s", (dtll_serv_id,))
        if not cursor.fetchone():
            return jsonify({"mensaje": "Uy, parece que no hay ningún servicio con ese ID"}), 404

        cursor.execute("SELECT cli_id FROM t_usuario JOIN t_cliente ON usu_id = cli_usu_id WHERE usu_num_doc = %s", (dtll_cli_num_doc,))
        dtll_cli_id = cursor.fetchone()
        if not dtll_cli_id:
            return jsonify({"mensaje": "Uy, parece que no hay ningún cliente con ese ID"}), 404

        cursor.execute("SELECT bar_id FROM t_usuario JOIN t_barbero ON usu_id = bar_usu_id WHERE usu_num_doc = %s", (dtll_bar_num_doc,))
        dtll_bar_id = cursor.fetchone()
        if not dtll_bar_id:
            return jsonify({"mensaje": "Uy, parece que no hay ningún barbero con ese ID"}), 404

        cursor.execute("INSERT INTO t_dtll_serv (dtll_serv_id, dtll_cli_id, dtll_bar_id) VALUES (%s, %s, %s)", (dtll_serv_id, dtll_cli_id, dtll_bar_id))
        cursor.connection.commit()
        return jsonify({"mensaje": "Se ha registrado el Detalle del Servicio Realizado"}), 200
    else:
        return jsonify({"mensaje": "Debe digitar todos los ID solicitados"}), 400

@detal_servicios_bp.route("/editarDetalleServicio/<dtll_id>", methods=["PUT"])
@token
def PUTdetalleServicio(dtll_id):
    data = request.get_json(silent=True)  
    if data is None:
        return jsonify({"error": "Error en la formacion del JSON"}), 400
    if 'dtll_serv_id' in request.json and 'dtll_cli_num_doc' in request.json and 'dtll_bar_num_doc' in request.json:
        dtll_serv_id = request.json["dtll_serv_id"]
        dtll_cli_num_doc = request.json["dtll_cli_num_doc"]
        dtll_bar_num_doc = request.json["dtll_bar_num_doc"]

        
        if not all([dtll_serv_id, dtll_cli_num_doc, dtll_bar_num_doc]): 
            return jsonify({"mensaje": "Faltan campos por rellenar"}), 400
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM t_dtll_serv WHERE dtll_id = %s",(dtll_id,))        
        if not cursor.fetchone():
            return({"mensaje" : "Uy, parece que no hay ningun detalle de servicio Realizado con ese ID"}), 404
        
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("SELECT * FROM t_servicio WHERE serv_id = %s", (dtll_serv_id,))
        if not cursor.fetchone():
            return jsonify({"mensaje": "Uy, parece que no hay ningún servicio con ese ID"}), 404

        cursor.execute("SELECT cli_id FROM t_usuario JOIN t_cliente ON usu_id = cli_usu_id WHERE usu_num_doc = %s", (dtll_cli_num_doc,))
        dtll_cli_id = cursor.fetchone()
        if not dtll_cli_id:
            return jsonify({"mensaje": "Uy, parece que no hay ningún cliente con ese ID"}), 404

        cursor.execute("SELECT bar_id FROM t_usuario JOIN t_barbero ON usu_id = bar_usu_id WHERE usu_num_doc = %s", (dtll_bar_num_doc,))
        dtll_bar_id = cursor.fetchone()
        if not dtll_bar_id:
            return jsonify({"mensaje": "Uy, parece que no hay ningún barbero con ese ID"}), 404

        cursor.execute("""
            UPDATE t_dtll_serv
            SET dtll_serv_id = %s, dtll_cli_id = %s, dtll_bar_id = %s
            WHERE dtll_id = %s
        """, (dtll_serv_id, dtll_cli_id, dtll_bar_id, dtll_id))
        cursor.connection.commit()
        return jsonify({"mensaje": "Se ha editado el Detalle del Servicio Realizado"}), 200
    else:
        return jsonify({"mensaje": "Debe digitar todos los ID solicitados"}), 400
