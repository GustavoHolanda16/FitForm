from datetime import datetime
from . import db
from flask_login import UserMixin
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
import json


class LogSistema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50)) 
    mensagem = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip = db.Column(db.String(50))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    altura = db.Column(db.Float, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(20))
    nivel_atividade = db.Column(db.String(50))  # sedentario, leve, moderado, intenso
    restricoes_alimentares = db.Column(db.Text)  # JSON com restrições
    preferencias_alimentares = db.Column(db.Text)  # JSON com preferências
    role = db.Column(db.String(20), default='user')
    
    # Relacionamentos
    objetivos = db.relationship('Objetivo', backref='user', lazy=True, cascade='all, delete-orphan')
    avaliacoes = db.relationship('Avaliacao', backref='user', lazy=True)
    treinos = db.relationship('Treino', backref='user', lazy=True)
    dietas = db.relationship('Dieta', backref='user', lazy=True)
    medidas = db.relationship('MedidaCorporal', backref='user', lazy=True)
    
    is_active = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    @property
    def imc(self):
        if self.altura > 0:
            return round(self.peso / (self.altura ** 2), 2)
        return 0
    
    @property
    def tmb(self):
        """Taxa Metabólica Basal (Harris-Benedict)"""
        if not self.idade or self.idade <= 0:
            return 0
            
        if self.genero == 'masculino':
            return 88.36 + (13.4 * self.peso) + (4.8 * self.altura * 100) - (5.7 * self.idade)
        else:
            return 447.6 + (9.2 * self.peso) + (3.1 * self.altura * 100) - (4.3 * self.idade)
    
    @property
    def idade(self):
        if self.data_nascimento:
            today = datetime.now().date()
            born = self.data_nascimento
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            return age
        return None
    
    def is_admin(self):
        return self.role == 'admin'
    
    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

class Objetivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    tipo = db.Column(db.String(50))  # perda_peso, ganho_massa, definicao, condicionamento
    meta = db.Column(db.String(100))  # ex: "perder 5kg"
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ativo')  # ativo, concluido, pausado
    progresso = db.Column(db.Float, default=0.0)  # 0-100%
    detalhes = db.Column(db.Text)  # JSON com metas semanais, KPIs, etc
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'meta': self.meta,
            'progresso': self.progresso,
            'data_fim': self.data_fim.strftime('%Y-%m-%d') if self.data_fim else None,
            'status': self.status
        }

class Dieta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    objetivo = db.Column(db.String(50))
    calorias_diarias = db.Column(db.Integer)
    plano_semanal = db.Column(db.Text)  # JSON com refeições
    lista_compras = db.Column(db.Text)  # JSON
    receitas = db.Column(db.Text)  # JSON
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    ativa = db.Column(db.Boolean, default=True)
    feedback = db.Column(db.Text)  # JSON com feedback do usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class MedidaCorporal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    peso = db.Column(db.Float)
    altura = db.Column(db.Float)
    braco_direito = db.Column(db.Float)
    braco_esquerdo = db.Column(db.Float)
    peitoral = db.Column(db.Float)
    cintura = db.Column(db.Float)
    quadril = db.Column(db.Float)
    coxa_direita = db.Column(db.Float)
    coxa_esquerda = db.Column(db.Float)
    panturrilha_direita = db.Column(db.Float)
    panturrilha_esquerda = db.Column(db.Float)
    percentual_gordura = db.Column(db.Float)
    foto_frontal = db.Column(db.String(200))  # caminho da imagem
    foto_lateral = db.Column(db.String(200))
    foto_posterior = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Classes existentes (atualizadas)
class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    peso = db.Column(db.Float)
    imc = db.Column(db.Float)
    calorias = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Treino(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    tipo = db.Column(db.String(100))
    objetivo = db.Column(db.String(100))
    nivel = db.Column(db.String(50))
    dias_semana = db.Column(db.Integer)
    detalhes = db.Column(db.Text)  # JSON com exercícios, séries, etc
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    feedback = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))