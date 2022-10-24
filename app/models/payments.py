from main import db
from sqlalchemy.orm import backref,relationship
from datetime import datetime


class Payments(db.Model):
    __tablename__='payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey('orders.id'))
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
   
    order = relationship("Orders", backref="payments")
    
    