from flask import Flask
from flask_mysqldb import MySQL  
from config import config
from package import routes

app = Flask(__name__)
app.config.from_object(config)
mysql = MySQL(app) 
app.mysql=mysql
routes(app)

#app.config['SECRET_KEY'] = "1234"

# Recuerden Arrancar en la ruta ("http://127.0.0.1:4000/") o ("http:://localhost:4000/")
# app.run(debug=True, port=4000, host="0.0.0.0")
