from main import db
from sqlalchemy.orm import backref
from datetime import datetime



class Orders(db.Model):
    __tablename__='orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    
    