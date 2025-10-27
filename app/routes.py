from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .forms import RegistroForm, LoginForm, GerarTreinoForm
from .models import User
from . import db
from .utils import gerar_treino_personalizado

main = Blueprint('main', __name__)

@main.route('/')
def home():
    user_id = session.get('user_id')
    if not user_id:
        flash('Você precisa fazer login primeiro.', 'warning')
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash('Usuário não encontrado. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    return render_template('home.html', user=user)


@main.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()
    if form.validate_on_submit():
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
            session['user_id'] = user.id
            flash(f'Bem-vindo, {user.nome}!', 'success')
            return redirect(url_for('main.home'))  # ✅ vai para a home
        else:
            flash('E-mail ou senha incorretos.', 'danger')
    return render_template('login.html', form=form)

@main.route('/gerar_treino', methods=['GET','POST'])
def gerar_treinos():
    form = GerarTreinoForm()

    if form.validate_on_submit():
        nivel = form.nivel.data
        objetivo = form.objetivo.data
        dias = form.dias.data

        treino = gerar_treino_personalizado(nivel,objetivo,dias)

        return render_template('treino_gerado.html', treino=treino)
    return render_template('gerar_treino.html', form=form)

@main.route('/usuarios')
def ver_usuarios():
    from.models import User
    usuarios = User.query.all()
    return '<br>'.join([f'{u.id} - {u.nome} - {u.email}' for u in usuarios])


@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.login'))
