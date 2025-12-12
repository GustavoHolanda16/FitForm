from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user
from . import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acesso Negado! Somente administradores podem acessar essa página!', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def log_acao(tipo, mensagem, user_id=None, ip=None):
    """Registra ação no sistema (mantido para compatibilidade)"""
    try:
        from .models import LogSistema
        log = LogSistema(
            tipo=tipo,
            mensagem=mensagem,
            user_id=user_id or (current_user.id if current_user.is_authenticated else None),
            ip=ip or (request.remote_addr if request else None)
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar log: {e}")

def log_acao_decorator(tipo):
    """Decorator para registrar ações"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            if current_user.is_authenticated:
                log_acao(
                    tipo=tipo,
                    mensagem=f"{current_user.email} executou {f.__name__}",
                    user_id=current_user.id,
                    ip=request.remote_addr
                )
            return result
        return decorated_function
    return decorator