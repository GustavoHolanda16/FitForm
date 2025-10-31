from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .forms import RegistroForm, LoginForm, GerarTreinoForm
from .models import User
from . import db
from .decorators import admin_required
from .utils import gerar_treino_personalizado
from flask_login import current_user, login_required, login_user, logout_user

main = Blueprint('main', __name__)

@main.before_request
def proteger_tudo():
    rota_livre = ['main.home','main.login','main.registro']
    if request.endpoint not in rota_livre and not current_user.is_authenticated:
        return redirect(url_for('main.login'))

@main.route('/')
def home():
    if not current_user.is_authenticated:
        flash('Você precisa fazer login primeiro.','warning')
        return redirect(url_for('main.login'))
    return render_template('home.html', user=current_user)

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este e-mail já está cadastrado.','danger')
            return render_template('registro.html', form=form)
        
        novo_user = User(
            nome=form.nome.data,
            email=form.email.data,
            senha=form.senha.data,
            altura=form.altura.data,
            peso=form.peso.data
        )
        db.session.add(novo_user)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('main.login'))
    return render_template('registro.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.senha == form.senha.data:
            login_user(user)
            flash(f'Bem-vindo, {user.nome}!', 'success')
            return redirect(url_for('main.perfil'))  # ✅ vai para a home
        else:
            flash('E-mail ou senha incorretos.', 'danger')
    return render_template('login.html', form=form)

@main.route('/gerar_treino', methods=['GET','POST'])
@login_required
def gerar_treinoo():
    form = GerarTreinoForm()

    if form.validate_on_submit():
        nivel = form.nivel.data
        objetivo = form.objetivo.data
        dias = form.dias.data

        treino = gerar_treino_personalizado(nivel,objetivo,dias)

        return render_template('treino_gerado.html', treino=treino)
    return render_template('gerar_treino.html', form=form)

@main.route('/usuarios')
@admin_required
def ver_usuarios():
    from.models import User
    usuarios = User.query.all()
    return '<br>'.join([f'{u.id} - {u.nome} - {u.email}' for u in usuarios])

@main.route('/perfil')
@login_required 
def perfil():
    return render_template('perfil.html', usuario= current_user)


@main.route('/logout')
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.login'))
