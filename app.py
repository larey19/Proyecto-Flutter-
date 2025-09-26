from flask import Flask
from flask_mysqldb import MySQL 
from config import config
from package import routes

app = Flask(__name__)
app.config.from_object(config)
mysql = MySQL(app) 
app.mysql=mysql
routes(app)


