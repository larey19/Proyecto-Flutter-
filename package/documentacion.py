from flask import  send_from_directory, render_template_string, Blueprint

documentacion_bp = Blueprint('documentacion', __name__)

@documentacion_bp.route('/swagger.json')
def swagger_json():
    return send_from_directory('.', 'swagger.json')

@documentacion_bp.route("/docs")
def swagger_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>API APRENDIZ</title>
      <link href="/static/swagger-ui/swagger-ui.css" rel="stylesheet" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="/static/swagger-ui/swagger-ui-bundle.js"></script>
      <script>
        const ui = SwaggerUIBundle({
          url: "./swagger.json",
          dom_id: '#swagger-ui',
        });
      </script>
    </body>
    </html>
    """)