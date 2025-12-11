from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, FloatField, 
                     SelectField, BooleanField, TextAreaField, DateField,
                     IntegerField, RadioField, MultipleFileField)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed

class RegistroForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired()])
    altura = FloatField('Altura (m)', validators=[DataRequired(), NumberRange(min=1.0, max=2.5)])
    peso = FloatField('Peso (kg)', validators=[DataRequired(), NumberRange(min=30, max=300)])
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[Optional()])
    genero = SelectField('Gênero', choices=[
        ('', 'Selecione...'),
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('outro', 'Outro')
    ], validators=[Optional()])
    nivel_atividade = SelectField('Nível de Atividade', choices=[
        ('sedentario', 'Sedentário (pouco ou nenhum exercício)'),
        ('leve', 'Leve (1-3 dias/semana)'),
        ('moderado', 'Moderado (3-5 dias/semana)'),
        ('ativo', 'Ativo (6-7 dias/semana)'),
        ('muito_ativo', 'Muito Ativo (exercício físico e trabalho físico)')
    ])
    submit = SubmitField('Criar Conta')

class ObjetivoForm(FlaskForm):
    titulo = StringField('Título do Objetivo', validators=[DataRequired()])
    tipo = SelectField('Tipo de Objetivo', choices=[
        ('perda_peso', '🎯 Perda de Peso'),
        ('ganho_massa', '💪 Ganho de Massa Muscular'),
        ('definicao', '✨ Definição Muscular'),
        ('condicionamento', '🏃 Condicionamento Físico'),
        ('forca', '🏋️ Aumento de Força'),
        ('resistencia', '🔥 Aumento de Resistência'),
        ('recomposicao', '🔄 Recomposição Corporal')
    ], validators=[DataRequired()])
    
    prazo = SelectField('Prazo', choices=[
        ('4', '4 semanas (1 mês)'),
        ('8', '8 semanas (2 meses)'),
        ('12', '12 semanas (3 meses)'),
        ('16', '16 semanas (4 meses)'),
        ('24', '24 semanas (6 meses)')
    ], validators=[DataRequired()])
    
    meta_especifica = StringField('Meta Específica (ex: perder 5kg)', 
                                  validators=[DataRequired()])
    
    prioridade = SelectField('Prioridade', choices=[
        ('alta', '🔥 Alta Prioridade'),
        ('media', '⚡ Média Prioridade'),
        ('baixa', '🌱 Baixa Prioridade')
    ])
    
    usar_ia = BooleanField('Usar IA para criar plano personalizado', default=True)
    
    observacoes = TextAreaField('Observações/Informações Adicionais')
    
    submit = SubmitField('Criar Objetivo')

class DietaForm(FlaskForm):
    nome = StringField('Nome da Dieta', validators=[DataRequired()])
    
    objetivo_associado = SelectField('Associar a Objetivo', coerce=int, 
                                     validators=[Optional()])
    
    tipo_dieta = SelectField('Tipo de Dieta', choices=[
        ('equilibrada', '🥗 Dieta Equilibrada'),
        ('low_carb', '🥑 Low Carb'),
        ('keto', '🥩 Cetogênica (Keto)'),
        ('mediterranea', '🐟 Mediterrânea'),
        ('vegetariana', '🌱 Vegetariana'),
        ('vegana', '🌿 Vegana'),
        ('high_protein', '🍗 Alta Proteína'),
        ('cutting', '✂️ Cutting (Definição)'),
        ('bulking', '📈 Bulking (Massa)')
    ], validators=[DataRequired()])
    
    restricoes = SelectField('Restrições Alimentares', choices=[
        ('nenhuma', 'Nenhuma'),
        ('lactose', 'Intolerância à Lactose'),
        ('gluten', 'Intolerância ao Glúten'),
        ('diabetico', 'Diabético'),
        ('hipertenso', 'Hipertenso'),
        ('alergia_amendoim', 'Alergia a Amendoim'),
        ('alergia_frutos_mar', 'Alergia a Frutos do Mar'),
        ('vegetariano', 'Vegetariano'),
        ('vegano', 'Vegano')
    ])
    
    preferencias = SelectField('Preferências', choices=[
        ('geral', 'Sem preferências específicas'),
        ('pratico', 'Refeições práticas'),
        ('cozinha', 'Gosto de cozinhar'),
        ('doces', 'Precisa incluir doces'),
        ('sal', 'Prefere comidas salgadas'),
        ('natural', 'Alimentos naturais'),
        ('industrializados', 'Aceita industrializados')
    ])
    
    calorias_diarias = IntegerField('Calorias Diárias (deixe 0 para cálculo automático)',
                                   validators=[Optional(), NumberRange(min=1000, max=5000)])
    
    usar_ia = BooleanField('Gerar com IA do Gemini', default=True)
    
    submit = SubmitField('Criar Dieta')

class MedidasForm(FlaskForm):
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    altura = FloatField('Altura (m)', validators=[Optional()])
    
    # Circunferências
    braco_direito = FloatField('Braço Direito (cm)', validators=[Optional()])
    braco_esquerdo = FloatField('Braço Esquerdo (cm)', validators=[Optional()])
    peitoral = FloatField('Peitoral (cm)', validators=[Optional()])
    cintura = FloatField('Cintura (cm)', validators=[Optional()])
    quadril = FloatField('Quadril (cm)', validators=[Optional()])
    coxa_direita = FloatField('Coxa Direita (cm)', validators=[Optional()])
    coxa_esquerda = FloatField('Coxa Esquerda (cm)', validators=[Optional()])
    
    # Fotos (opcional)
    foto_frontal = FileField('Foto Frontal', 
                           validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens!')])
    foto_lateral = FileField('Foto Lateral', 
                           validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens!')])
    
    observacoes = TextAreaField('Observações')
    
    submit = SubmitField('Salvar Medidas')

    # Adicione no final do arquivo forms.py:

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class GerarTreinoForm(FlaskForm):
    nivel = SelectField('Nível', choices=[
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado')
    ], validators=[DataRequired()])
    
    objetivo = SelectField('Objetivo', choices=[
        ('hipertrofia', 'Hipertrofia (Massa)'),
        ('forca', 'Força'),
        ('resistencia', 'Resistência'),
        ('emagrecimento', 'Emagrecimento'),
        ('condicionamento', 'Condicionamento Geral')
    ], validators=[DataRequired()])
    
    dias = SelectField('Dias por Semana', choices=[
        ('3', '3 dias'),
        ('4', '4 dias'),
        ('5', '5 dias'),
        ('6', '6 dias')
    ], validators=[DataRequired()])
    
    historico = TextAreaField('Histórico/Lesões/Preferências', validators=[Optional()])
    usar_ia = BooleanField('Usar IA para personalização avançada', default=True)
    submit = SubmitField('Gerar Treino')