from sqlalchemy.orm import backref
from main import db
from datetime import datetime



class Stock(db.Model):
    __tablename__='stock'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantity = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    
    
    def __repr__(self):
        return '<Stock %r>' % self.id
    
    