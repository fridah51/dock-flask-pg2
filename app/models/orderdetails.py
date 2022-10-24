from main import db
from sqlalchemy.orm import backref,relationship
from datetime import datetime


class OrderDetails(db.Model):
    __tablename__='orderdetails'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    pid = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    current_bp = db.Column(db.Integer,  nullable=True)
    current_sp = db.Column(db.Integer, nullable=True)
    
    order = relationship("Orders", backref="orderdetails")
    od = relationship("Products", backref="orderdetails")