from main import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView  
from flask_login import UserMixin
from datetime import datetime


class Users(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100),nullable=False, unique=True)
    password = db.Column(db.String(100), server_default='')
    username = db.Column(db.String(1000))
    role = db.Column(db.String(1000))
   
    
   

    