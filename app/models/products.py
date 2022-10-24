from main import db
from sqlalchemy.orm import backref,relationship


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    bp = db.Column(db.Integer,  nullable=False)
    sp = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
 
    # def __repr__(self):
    #     return '<Products %r>' % self.name
    
   