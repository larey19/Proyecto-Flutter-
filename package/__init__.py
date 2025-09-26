from .usuarios import usuarios_bp
from .clientes import clientes_bp
from .barberos import barberos_bp
from .servicios import servicios_bp
from .detalle_servicio import detal_servicios_bp
from .documentacion import documentacion_bp
from .reservas import reservas_bp
from .login import login_bp

def routes(app):
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(barberos_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(detal_servicios_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(documentacion_bp)

