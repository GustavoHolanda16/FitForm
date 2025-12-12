# Crie um script para recriar o banco
# recriar_db.py
from app import create_app, db
from app.models import User, Objetivo, Dieta, Treino, MedidaCorporal, Avaliacao, LogSistema

app = create_app()

with app.app_context():
    # Drop todas as tabelas
    db.drop_all()
    
    # Crie todas as tabelas
    db.create_all()
    
    print("✅ Banco de dados recriado com sucesso!")
    print("Tabelas criadas:")
    print("- User")
    print("- Objetivo") 
    print("- Dieta")
    print("- Treino")
    print("- MedidaCorporal")
    print("- Avaliacao")
    print("- LogSistema")