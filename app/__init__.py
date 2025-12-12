from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os 

db = SQLAlchemy()
login_manager = LoginManager()

def clamp_filter(value, min_value, max_value):
    """Filtro Jinja2 para limitar valor entre mínimo e máximo."""
    return max(min_value, min(value, max_value))

def create_app():
    # Criar instância do app
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fitform-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fitform.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ✅ ADICIONAR ESTA LINHA: Registrar o filtro no Jinja2
    app.jinja_env.filters['clamp'] = clamp_filter
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    from .routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
    
    return app