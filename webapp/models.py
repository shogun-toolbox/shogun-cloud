from flask.ext import sqlalchemy
from datetime import datetime
from flask.ext.login import UserMixin

db = sqlalchemy.SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    container_id = db.Column(db.String(255))
    registered_on = db.Column(db.DateTime, nullable=False,
                              default=db.func.now(),
                              server_default=db.func.now())
    
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.registered_on = datetime.utcnow()

