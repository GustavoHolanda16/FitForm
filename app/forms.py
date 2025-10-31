from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length


class RegistroForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    altura = FloatField('Altura (m)', validators=[DataRequired()])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    submit = SubmitField('Registrar')

class LoginForm(FlaskForm) :
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha',validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Entrar')

class GerarTreinoForm(FlaskForm):
    nivel = SelectField('Nível', choices=[
        ('1','Básico'),
        ('2','Intermediário'),
        ('3','Avançado')
    ], validators=[DataRequired()])

    objetivo = SelectField('Objetivo', choices=[
        ('1','Hipertrofia'),
        ('2', 'Perda de Peso'),
        ('3','Condicionamento Físico')
    ], validators=[DataRequired()])

    dias = SelectField('Quantidade de dias por semana', choices=[
        ('3', '3 dias'),
        ('5', '5 dias')
    ], validators=[DataRequired()])

    submit = SubmitField('Gerar Treino')
    