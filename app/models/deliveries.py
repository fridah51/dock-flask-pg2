from main import db
from sqlalchemy.orm import backref,relationship
from datetime import datetime


class Deliveries(db.Model):
    __tablename__='deliveries'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    customer_name = db.Column(db.String(80),  nullable=False )
    phone_no = db.Column(db.String(10), unique=True, nullable=False )
    address = db.Column(db.String(80), nullable=False)
    delivered_by = db.Column(db.String(80),  nullable=False )
    date_delivered = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    
    order = relationship("Orders", backref="deliveries")