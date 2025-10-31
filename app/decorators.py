from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash ('Acesso Negado! Somente administradores podem acessar essa página!','danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function