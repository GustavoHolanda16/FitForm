from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from .models import User, Objetivo, Dieta, Treino, MedidaCorporal, Avaliacao, LogSistema
from . import db
from .decorators import admin_required
from .utils import gerar_treino_personalizado
from .objetivos_service import ObjetivoService
from .dieta_service import DietaService
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
from .forms import RegistroForm, ObjetivoForm, DietaForm, MedidasForm, LoginForm, GerarTreinoForm

main = Blueprint('main', __name__)

def log_acao(tipo, mensagem):
    """Registra ação no sistema"""
    try:
        log = LogSistema(
            tipo=tipo,
            mensagem=mensagem,
            user_id=current_user.id if current_user.is_authenticated else None,
            ip=request.remote_addr if request else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar log: {e}")

# ==================== MIDDLEWARES ====================
@main.before_request
def proteger_tudo():
    """Protege todas as rotas exceto as públicas"""
    rotas_livres = [
        'main.home', 
        'main.login', 
        'main.registro',
        'main.logout',
        'static'  # Para arquivos estáticos
    ]
    
    if request.endpoint not in rotas_livres and not current_user.is_authenticated:
        flash('Você precisa fazer login primeiro.', 'warning')
        return redirect(url_for('main.login'))

@main.before_app_request
def atualizar_ultimo_login():
    """Atualiza o último login do usuário"""
    if current_user.is_authenticated:
        try:
            current_user.ultimo_login = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            print(f"Erro ao atualizar último login: {e}")

# ==================== ROTAS PÚBLICAS ====================
@main.route('/')
def home():
    """Página inicial"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de novo usuário"""
    form = RegistroForm()
    
    if form.validate_on_submit():
        try:
            # Verificar se email já existe
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Este e-mail já está cadastrado.', 'danger')
                return render_template('registro.html', form=form)
            
            # Verificar se senhas coincidem
            if form.senha.data != form.confirmar_senha.data:
                flash('As senhas não coincidem.', 'danger')
                return render_template('registro.html', form=form)
            
            # Criar novo usuário
            novo_user = User(
                nome=form.nome.data,
                email=form.email.data,
                senha_hash=generate_password_hash(form.senha.data),
                altura=form.altura.data,
                peso=form.peso.data,
                data_nascimento=form.data_nascimento.data,
                genero=form.genero.data,
                nivel_atividade=form.nivel_atividade.data,
                role='user',
                is_active=True,
                data_criacao=datetime.utcnow()
            )
            
            db.session.add(novo_user)
            db.session.commit()
            
            # Registrar log
            log_acao('registro', f'Novo usuário registrado: {form.email.data}')
            
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar conta: {str(e)}', 'danger')
    
    return render_template('registro.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            
            # Verificar se usuário existe e senha está correta
            if user and check_password_hash(user.senha_hash, form.senha.data):
                # Verificar se conta está ativa
                if not user.is_active:
                    flash('Sua conta está desativada. Entre em contato com o administrador.', 'danger')
                    return render_template('login.html', form=form)
                
                login_user(user, remember=form.remember.data)
                
                # Registrar log
                log_acao('login', f'Usuário fez login: {user.email}')
                
                flash(f'Bem-vindo de volta, {user.nome}!', 'success')
                
                # Redirecionar para a página que tentava acessar ou dashboard
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.dashboard'))
            else:
                flash('E-mail ou senha incorretos.', 'danger')
                
        except Exception as e:
            flash(f'Erro ao fazer login: {str(e)}', 'danger')
    
    return render_template('login.html', form=form)

# ==================== ROTAS AUTENTICADAS ====================
@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard do usuário"""
    try:
        # Obter objetivos do usuário
        objetivos = current_user.objetivos.all() if hasattr(current_user, 'objetivos') else []
        objetivos_ativos = [obj for obj in objetivos if obj.status == 'ativo']
        
        # Obter dietas
        dietas = current_user.dietas.all() if hasattr(current_user, 'dietas') else []
        dieta_ativa = next((d for d in dietas if d.ativa), None)
        
        # Obter medidas
        medidas = []
        if hasattr(current_user, 'medidas'):
            medidas = current_user.medidas.order_by(MedidaCorporal.data.desc()).limit(10).all()
        
        # Calcular treinos ativos
        treinos_ativos = 0
        if hasattr(current_user, 'treinos'):
            treinos_ativos = len(current_user.treinos.filter_by(ativo=True).all())
        
        # Criar dicionário 'dados' para passar ao template
        dados = {
            'usuario': current_user,
            'objetivos_ativos': objetivos_ativos,
            'dieta_ativa': dieta_ativa,
            'treinos_ativos': treinos_ativos,
            'proximo_treino': 'Hoje 18:00',  # Valor padrão ou implementar lógica real
            'proxima_refeicao': 'Almoço 12:30',  # Valor padrão
            'compromissos': [
                {'titulo': 'Treino de Força', 'hora': '18:00', 'icone': 'bi-activity'},
                {'titulo': 'Refeição #4', 'hora': '15:00', 'icone': 'bi-egg-fried'},
                {'titulo': 'Meta de Água', 'hora': '2.5L', 'icone': 'bi-droplet'}
            ]
        }
        
        # Calcular total de objetivos
        total_objetivos = len(objetivos)
        objetivos_concluidos = len([obj for obj in objetivos if obj.status == 'concluido'])
        
        # Gerar insights da IA
        insights = "Continue registrando seus treinos e dietas para receber insights personalizados."
        
        return render_template('dashboard.html',
                             objetivos=objetivos,
                             dados=dados,
                             insights=insights,
                             total_objetivos=total_objetivos,
                             objetivos_concluidos=objetivos_concluidos)
                             
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return redirect(url_for('main.home'))

@main.route('/perfil')
@login_required
def perfil():
    """Página de perfil do usuário"""
    try:
        # Buscar dados recentes
        objetivos = Objetivo.query.filter_by(
            user_id=current_user.id
        ).order_by(Objetivo.data_inicio.desc()).limit(3).all()
        
        treinos = Treino.query.filter_by(
            user_id=current_user.id, 
            ativo=True
        ).limit(3).all()
        
        dieta_ativa = Dieta.query.filter_by(
            user_id=current_user.id, 
            ativa=True
        ).first()
        
        medidas_recentes = MedidaCorporal.query.filter_by(
            user_id=current_user.id
        ).order_by(MedidaCorporal.data.desc()).first()
        
        return render_template('perfil.html',
                             usuario=current_user,
                             objetivos=objetivos,
                             treinos=treinos,
                             dieta_ativa=dieta_ativa,
                             medidas_recentes=medidas_recentes)
    except Exception as e:
        flash(f'Erro ao carregar perfil: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

# ==================== OBJETIVOS ====================
@main.route('/objetivos', methods=['GET', 'POST'])
@login_required
def objetivos():
    """Gerenciar objetivos do usuário"""
    form = ObjetivoForm()
    objetivo_service = ObjetivoService()
    
    # Carregar objetivos existentes
    objetivos = Objetivo.query.filter_by(user_id=current_user.id).all()
    
    if form.validate_on_submit():
        try:
            # Preparar dados do usuário
            usuario_data = {
                "nome": current_user.nome,
                "idade": current_user.idade,
                "altura": current_user.altura,
                "peso": current_user.peso,
                "genero": current_user.genero,
                "nivel_atividade": current_user.nivel_atividade,
                "imc": current_user.imc
            }
            
            if form.usar_ia.data:
                # Criar objetivo com IA
                objetivo_data = objetivo_service.criar_objetivo_personalizado(
                    usuario_data=usuario_data,
                    objetivo_tipo=form.tipo.data,
                    prazo_semanas=int(form.prazo.data)
                )
            else:
                # Criar objetivo manual
                objetivo_data = {
                    "titulo": form.titulo.data,
                    "tipo": form.tipo.data,
                    "meta": form.meta_especifica.data,
                    "prazo_semanas": int(form.prazo.data)
                }
            
            # Calcular data de término
            data_fim = datetime.utcnow() + timedelta(weeks=int(form.prazo.data))
            
            # Salvar no banco
            novo_objetivo = Objetivo(
                titulo=form.titulo.data,
                descricao=form.observacoes.data,
                tipo=form.tipo.data,
                meta=form.meta_especifica.data,
                data_fim=data_fim,
                detalhes=json.dumps(objetivo_data),
                user_id=current_user.id
            )
            
            db.session.add(novo_objetivo)
            db.session.commit()
            
            log_acao('criar_objetivo', f'Criou objetivo: {form.titulo.data}')
            
            flash('Objetivo criado com sucesso!', 'success')
            return redirect(url_for('main.detalhe_objetivo', objetivo_id=novo_objetivo.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar objetivo: {str(e)}', 'danger')
    
    return render_template('objetivos.html', form=form, objetivos=objetivos)

@main.route('/objetivo/<int:objetivo_id>')
@login_required
def detalhe_objetivo(objetivo_id):
    """Detalhes de um objetivo específico"""
    try:
        objetivo = Objetivo.query.get_or_404(objetivo_id)
        
        # Verificar permissão
        if objetivo.user_id != current_user.id and not current_user.is_admin():
            flash('Acesso negado!', 'danger')
            return redirect(url_for('main.objetivos'))
        
        # Carregar detalhes
        detalhes = {}
        if objetivo.detalhes:
            try:
                detalhes = json.loads(objetivo.detalhes)
            except json.JSONDecodeError:
                detalhes = {"error": "Dados corrompidos"}
        
        # Carregar medidas relacionadas
        medidas = MedidaCorporal.query.filter_by(user_id=current_user.id)\
            .filter(MedidaCorporal.data >= objetivo.data_inicio)\
            .order_by(MedidaCorporal.data).all()
        
        return render_template('detalhe_objetivo.html',
                             objetivo=objetivo,
                             detalhes=detalhes,
                             medidas=medidas)
    except Exception as e:
        flash(f'Erro ao carregar objetivo: {str(e)}', 'danger')
        return redirect(url_for('main.objetivos'))

# ==================== DIETAS ====================
@main.route('/dietas', methods=['GET', 'POST'])
@login_required
def dietas():
    """Gerenciar dietas do usuário"""
    form = DietaForm()
    
    # Carregar objetivos para associação
    objetivos_ativos = Objetivo.query.filter_by(
        user_id=current_user.id, 
        status='ativo'
    ).all()
    
    form.objetivo_associado.choices = [('', 'Não associar')] + \
        [(o.id, o.titulo) for o in objetivos_ativos]
    
    # Carregar dietas existentes
    dietas_ativas = Dieta.query.filter_by(
        user_id=current_user.id, 
        ativa=True
    ).all()
    
    dietas_anteriores = Dieta.query.filter_by(
        user_id=current_user.id, 
        ativa=False
    ).all()
    
    if form.validate_on_submit():
        try:
            dieta_service = DietaService()
            
            # Preparar dados do usuário
            usuario_data = {
                "nome": current_user.nome,
                "idade": current_user.idade,
                "altura": current_user.altura,
                "peso": current_user.peso,
                "genero": current_user.genero,
                "nivel_atividade": current_user.nivel_atividade,
                "imc": current_user.imc
            }
            
            if form.usar_ia.data:
                # Buscar objetivo associado
                objetivo_data = {}
                if form.objetivo_associado.data:
                    objetivo = Objetivo.query.get(form.objetivo_associado.data)
                    if objetivo:
                        objetivo_data = {
                            "tipo": objetivo.tipo,
                            "meta": objetivo.meta
                        }
                
                # Gerar dieta com IA
                plano_dieta = dieta_service.criar_dieta_personalizada(
                    usuario_data=usuario_data,
                    objetivo=form.tipo_dieta.data,
                    restricoes=form.restricoes.data,
                    preferencias=form.preferencias.data
                )
            else:
                # Dieta básica
                plano_dieta = {
                    "calorias_diarias": form.calorias_diarias.data or 2000,
                    "tipo": form.tipo_dieta.data
                }
            
            # Salvar no banco
            nova_dieta = Dieta(
                nome=form.nome.data,
                objetivo=form.tipo_dieta.data,
                calorias_diarias=plano_dieta.get('calorias_diarias', 2000),
                plano_semanal=json.dumps(plano_dieta.get('plano_semanal', {})),
                lista_compras=json.dumps(plano_dieta.get('lista_compras', [])),
                receitas=json.dumps(plano_dieta.get('receitas_especiais', [])),
                user_id=current_user.id
            )
            
            if form.objetivo_associado.data:
                nova_dieta.objetivo_associado = form.objetivo_associado.data
            
            db.session.add(nova_dieta)
            db.session.commit()
            
            log_acao('criar_dieta', f'Criou dieta: {form.nome.data}')
            
            flash('Dieta criada com sucesso!', 'success')
            return redirect(url_for('main.detalhe_dieta', dieta_id=nova_dieta.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar dieta: {str(e)}', 'danger')
    
    return render_template('dietas.html',
                         form=form,
                         dietas_ativas=dietas_ativas,
                         dietas_anteriores=dietas_anteriores)

@main.route('/dieta/<int:dieta_id>')
@login_required
def detalhe_dieta(dieta_id):
    """Detalhes de uma dieta específica"""
    try:
        dieta = Dieta.query.get_or_404(dieta_id)
        
        # Verificar permissão
        if dieta.user_id != current_user.id and not current_user.is_admin():
            flash('Acesso negado!', 'danger')
            return redirect(url_for('main.dietas'))
        
        # Parse JSON com tratamento de erros
        plano_semanal = {}
        lista_compras = []
        receitas = []
        
        try:
            if dieta.plano_semanal:
                plano_semanal = json.loads(dieta.plano_semanal)
        except json.JSONDecodeError:
            plano_semanal = {"error": "Dados do plano semanal corrompidos"}
        
        try:
            if dieta.lista_compras:
                lista_compras = json.loads(dieta.lista_compras)
        except json.JSONDecodeError:
            lista_compras = ["Erro ao carregar lista de compras"]
        
        try:
            if dieta.receitas:
                receitas = json.loads(dieta.receitas)
        except json.JSONDecodeError:
            receitas = ["Erro ao carregar receitas"]
        
        return render_template('detalhe_dieta.html',
                             dieta=dieta,
                             plano_semanal=plano_semanal,
                             lista_compras=lista_compras,
                             receitas=receitas)
    except Exception as e:
        flash(f'Erro ao carregar dieta: {str(e)}', 'danger')
        return redirect(url_for('main.dietas'))

# ==================== MEDIDAS ====================
@main.route('/medidas', methods=['GET', 'POST'])
@login_required
def medidas():
    """Registrar novas medidas"""
    form = MedidasForm()
    
    # Carregar histórico
    historico_medidas = MedidaCorporal.query\
        .filter_by(user_id=current_user.id)\
        .order_by(MedidaCorporal.data.desc())\
        .limit(10)\
        .all()
    
    if form.validate_on_submit():
        try:
            # Processar upload de fotos
            foto_frontal_path = None
            foto_lateral_path = None
            
            if form.foto_frontal.data:
                foto = form.foto_frontal.data
                filename = f"frontal_{current_user.id}_{datetime.now().timestamp()}.jpg"
                # Certifique-se que o diretório existe
                upload_dir = os.path.join('app', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                foto_frontal_path = os.path.join('static/uploads', filename)
                foto.save(os.path.join('app', foto_frontal_path))
            
            if form.foto_lateral.data:
                foto = form.foto_lateral.data
                filename = f"lateral_{current_user.id}_{datetime.now().timestamp()}.jpg"
                upload_dir = os.path.join('app', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                foto_lateral_path = os.path.join('static/uploads', filename)
                foto.save(os.path.join('app', foto_lateral_path))
            
            # Salvar medidas
            novas_medidas = MedidaCorporal(
                peso=form.peso.data,
                altura=form.altura.data or current_user.altura,
                braco_direito=form.braco_direito.data,
                braco_esquerdo=form.braco_esquerdo.data,
                peitoral=form.peitoral.data,
                cintura=form.cintura.data,
                quadril=form.quadril.data,
                coxa_direita=form.coxa_direita.data,
                coxa_esquerda=form.coxa_esquerda.data,
                foto_frontal=foto_frontal_path,
                foto_lateral=foto_lateral_path,
                observacoes=form.observacoes.data,
                user_id=current_user.id
            )
            
            # Atualizar peso do usuário
            if form.peso.data != current_user.peso:
                current_user.peso = form.peso.data
            
            db.session.add(novas_medidas)
            db.session.add(current_user)
            db.session.commit()
            
            log_acao('registrar_medidas', f'Registrou novas medidas: {form.peso.data}kg')
            
            flash('Medidas salvas com sucesso!', 'success')
            return redirect(url_for('main.progresso'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar medidas: {str(e)}', 'danger')
    
    return render_template('medidas.html',
                         form=form,
                         historico=historico_medidas)

@main.route('/progresso')
@login_required
def progresso():
    """Página de acompanhamento de progresso"""
    try:
        medidas = MedidaCorporal.query\
            .filter_by(user_id=current_user.id)\
            .order_by(MedidaCorporal.data)\
            .all()
        
        objetivos = Objetivo.query\
            .filter_by(user_id=current_user.id)\
            .order_by(Objetivo.data_inicio.desc())\
            .all()
        
        # Calcular estatísticas
        variacao_peso = variacao_imc = 0
        
        if medidas:
            primeira_medida = medidas[0]
            ultima_medida = medidas[-1]
            
            variacao_peso = ultima_medida.peso - primeira_medida.peso
            
            if primeira_medida.altura > 0 and ultima_medida.altura > 0:
                imc_inicial = primeira_medida.peso / (primeira_medida.altura ** 2)
                imc_atual = ultima_medida.peso / (ultima_medida.altura ** 2)
                variacao_imc = imc_atual - imc_inicial
        
        return render_template('progresso.html',
                             medidas=medidas,
                             objetivos=objetivos,
                             variacao_peso=variacao_peso,
                             variacao_imc=variacao_imc)
    except Exception as e:
        flash(f'Erro ao carregar progresso: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

# ==================== TREINOS ====================
@main.route('/gerar_treino', methods=['GET', 'POST'])
@login_required
def gerar_treino():
    """Gerar treino personalizado (sistema base)"""
    form = GerarTreinoForm()
    
    if form.validate_on_submit():
        try:
            nivel = form.nivel.data
            objetivo = form.objetivo.data
            dias = form.dias.data
            
            treino = gerar_treino_personalizado(nivel, objetivo, dias, usar_ia=False)
            
            # Salvar treino gerado
            novo_treino = Treino(
                nome=f"Treino {nivel}-{objetivo}",
                tipo=objetivo,
                objetivo=objetivo,
                nivel=nivel,
                dias_semana=int(dias),
                detalhes=json.dumps(treino),
                user_id=current_user.id
            )
            
            db.session.add(novo_treino)
            db.session.commit()
            
            log_acao('gerar_treino', f'Gerou treino: {nivel}-{objetivo}')
            
            return render_template('treino_gerado.html', treino=treino)
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao gerar treino: {str(e)}', 'danger')
    
    return render_template('gerar_treino.html', form=form)

@main.route('/gerar_treino_ia', methods=['GET', 'POST'])
@login_required
def gerar_treino_ia():
    """Gerar treino com IA"""
    form = GerarTreinoForm()
    
    if form.validate_on_submit():
        try:
            nivel = form.nivel.data
            objetivo = form.objetivo.data
            dias = form.dias.data
            usar_ia = True
            historico = form.historico.data if hasattr(form, 'historico') else ""
            
            # Buscar histórico do usuário
            avaliacoes = Avaliacao.query.filter_by(user_id=current_user.id)\
                .order_by(Avaliacao.data.desc()).all()
            
            historico_completo = f"""
            Usuário: {current_user.nome}
            Altura: {current_user.altura}m
            Peso atual: {current_user.peso}kg
            Histórico de avaliações: {[(a.peso, a.data.strftime('%Y-%m-%d')) for a in avaliacoes[:3]]}
            Informações adicionais: {historico}
            """
            
            treino = gerar_treino_personalizado(
                nivel=nivel,
                objetivo=objetivo,
                dias=dias,
                usar_ia=usar_ia,
                historico=historico_completo
            )
            
            # Salvar treino gerado no banco
            novo_treino = Treino(
                nome=f"Treino {nivel}-{objetivo}",
                tipo=objetivo,
                objetivo=objetivo,
                nivel=nivel,
                dias_semana=int(dias),
                detalhes=json.dumps(treino),
                user_id=current_user.id
            )
            
            db.session.add(novo_treino)
            db.session.commit()
            
            log_acao('gerar_treino_ia', f'Gerou treino com IA: {nivel}-{objetivo}')
            
            return render_template('treino_gerado.html',
                                 treino=treino,
                                 usar_ia=usar_ia,
                                 form=form)
                                 
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao gerar treino com IA: {str(e)}', 'danger')
    
    return render_template('gerar_treino.html', form=form)

@main.route('/analise_ia')
@login_required
def analise_ia():
    """Análise de desempenho com IA"""
    try:
        from .gemini_service import GeminiService
        
        avaliacoes = Avaliacao.query.filter_by(user_id=current_user.id).all()
        medidas = MedidaCorporal.query.filter_by(user_id=current_user.id).all()
        
        dados_usuario = {
            "nome": current_user.nome,
            "idade": current_user.idade,
            "altura": current_user.altura,
            "peso_atual": current_user.peso,
            "genero": current_user.genero,
            "nivel_atividade": current_user.nivel_atividade,
            "historico_peso": [{"peso": a.peso, "data": a.data.strftime('%Y-%m-%d')} for a in avaliacoes],
            "historico_medidas": [{"cintura": m.cintura, "data": m.data.strftime('%Y-%m-%d')} for m in medidas if m.cintura],
            "imc_atual": current_user.imc if hasattr(current_user, 'imc') else 0
        }
        
        gemini = GeminiService()
        analise = gemini.analisar_desempenho(str(dados_usuario))
        
        return render_template('analise_ia.html',
                             analise=analise,
                             dados=dados_usuario)
    except ImportError:
        flash('Serviço de IA não disponível no momento.', 'warning')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        flash(f'Erro ao gerar análise: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

# ==================== ADMIN ====================
@main.route('/admin/usuarios')
@admin_required
def ver_usuarios():
    """Lista de usuários (admin)"""
    try:
        usuarios = User.query.all()
        return render_template('admin/usuarios_lista.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Erro ao carregar usuários: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))

# ==================== UTILITÁRIOS ====================
@main.route('/logout')
def logout():
    """Logout do usuário"""
    if current_user.is_authenticated:
        log_acao('logout', f'Usuário fez logout: {current_user.email}')
    
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.login'))

@main.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    """Configurações da conta"""
    if request.method == 'POST':
        try:
            # Atualizar preferências
            current_user.restricoes_alimentares = request.form.get('restricoes', '')
            current_user.preferencias_alimentares = request.form.get('preferencias', '')
            
            db.session.commit()
            flash('Configurações atualizadas!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar configurações: {str(e)}', 'danger')
    
    return render_template('configuracoes.html', usuario=current_user)

# ==================== API PARA DADOS ====================
@main.route('/api/medidas')
@login_required
def api_medidas():
    """API para dados de medidas (para gráficos)"""
    try:
        medidas = MedidaCorporal.query\
            .filter_by(user_id=current_user.id)\
            .order_by(MedidaCorporal.data)\
            .all()
        
        dados = {
            'datas': [m.data.strftime('%Y-%m-%d') for m in medidas],
            'pesos': [m.peso for m in medidas],
            'cinturas': [m.cintura for m in medidas if m.cintura],
            'quadris': [m.quadril for m in medidas if m.quadril]
        }
        
        return jsonify(dados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/estatisticas')
@login_required
def api_estatisticas():
    """API para estatísticas do usuário"""
    try:
        total_objetivos = Objetivo.query.filter_by(user_id=current_user.id).count()
        objetivos_concluidos = Objetivo.query.filter_by(
            user_id=current_user.id,
            status='concluido'
        ).count()
        
        total_treinos = Treino.query.filter_by(user_id=current_user.id).count()
        treinos_ativos = Treino.query.filter_by(
            user_id=current_user.id,
            ativo=True
        ).count()
        
        primeira_medida = MedidaCorporal.query\
            .filter_by(user_id=current_user.id)\
            .order_by(MedidaCorporal.data)\
            .first()
        
        ultima_medida = MedidaCorporal.query\
            .filter_by(user_id=current_user.id)\
            .order_by(MedidaCorporal.data.desc())\
            .first()
        
        # Calcular porcentagem com segurança
        porcentagem_objetivos = 0
        if total_objetivos > 0:
            porcentagem_objetivos = (objetivos_concluidos / total_objetivos) * 100
        
        estatisticas = {
            'objetivos': {
                'total': total_objetivos,
                'concluidos': objetivos_concluidos,
                'porcentagem': round(porcentagem_objetivos, 2)
            },
            'treinos': {
                'total': total_treinos,
                'ativos': treinos_ativos
            },
            'peso': {
                'inicial': primeira_medida.peso if primeira_medida else current_user.peso,
                'atual': ultima_medida.peso if ultima_medida else current_user.peso,
                'variacao': (ultima_medida.peso - primeira_medida.peso) if primeira_medida and ultima_medida else 0
            }
        }
        
        return jsonify(estatisticas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PÁGINAS DE ERRO ====================
@main.app_errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template('errors/404.html'), 404

@main.app_errorhandler(403)
def acesso_negado(error):
    return render_template('errors/403.html'), 403

@main.app_errorhandler(500)
def erro_servidor(error):
    return render_template('errors/500.html'), 500

# ==================== FUNÇÕES AUXILIARES ====================
def calcular_imc(peso, altura):
    """Calcula o IMC"""
    if altura > 0:
        return peso / (altura ** 2)
    return 0

def formatar_data(data):
    """Formata data para exibição"""
    if data:
        return data.strftime('%d/%m/%Y')
    return ''