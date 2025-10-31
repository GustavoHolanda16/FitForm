from . import db
from datetime import datetime
from flask_login import UserMixin
from . import login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    altura = db.Column(db.Float, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    role = db.Column(db.String(20), default='user')
    avaliacoes = db.relationship('Avaliacao', backref ='user', lazy=True)
    treinos = db.relationship('Treino', backref = 'user', lazy=True)
  
    def is_admin(self):
        return self.role == 'admin'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    peso = db.Column(db.Float)
    imc = db.Column(db.Float)
    calorias = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Treino(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100))
    objetivo = db.Column(db.String(100))
    exercicio = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
