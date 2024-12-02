from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

# Configurar la conexión a MongoDB

client = MongoClient('localhost', 27017)
db = client.tienda_virtual

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Desactiva el caché para propósitos de desarrollo

from app import routes
