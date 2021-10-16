import psycopg2
import psycopg2.extensions
from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime, time

con = psycopg2.connect(
    host="localhost",
    database="sch_95",
    user="postgres",
    password="762341Aa")

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


DB_URL = 'postgresql://postgres:762341Aa@localhost:6432/sch_95'
UPLOAD_FOLDER = r'/home/armianin/sites_100%/sch_95/static'
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['GOOGLEMAPS_KEY'] = "XXX"
app.config['RECAPTCHA_USE_SSL']= False
app.config['RECAPTCHA_PUBLIC_KEY'] ='6LeBCfIZAAAAAO39_L4Gd7f6uCM0PfP_N3XjHxkW'
app.config['RECAPTCHA_PRIVATE_KEY'] ='6LeBCfIZAAAAAJTjq0Xz_ndAW9LByCo1nJJKy'
app.config['RECAPTCHA_OPTIONS'] = {'theme':'black'}
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db_cursor = con.cursor()

class Item(db.Model):
    __tablename__ = 'main'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    img = db.Column(db.ARRAY(db.TEXT), nullable=False)
    text = db.Column(db.String, nullable=False)
    creator_name = db.Column(db.String(), nullable=False)
    def __init__(self, title, img, text, creator_name):
        self.img = img
        self.text = text
        self.title = title
        self.creator_name = creator_name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name, password):
        self.name = name
        self.password = password


