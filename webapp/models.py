from flask.ext import sqlalchemy

db = sqlalchemy.SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    container_id = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False,
                              default=db.func.now(),
                              server_default=db.func.now())

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
