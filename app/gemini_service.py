import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
        
        try:
            genai.configure(api_key=api_key)
            
            # ✅ Modelos atuais disponíveis - experimente estas opções em ordem:
            
            # Opção 1: Modelo mais comum e estável
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            # Opção 2: Modelo Pro (mais capaz)
            # self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
            
            # Opção 3: Modelo mais novo (pode requerer API atualizada)
            # self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            print(f"✅ Gemini Service inicializado com modelo: {self.model.model_name}")
            
        except Exception as e:
            raise ValueError(f"❌ ERRO ao inicializar Gemini: {e}")
    
    def gerar_treino_ia(self, nivel, objetivo, dias, historico=""):
        """Gera treino personalizado com IA (SEMPRE usa IA)"""
        prompt = f"""
        Como personal trainer IA, gere um plano de treino personalizado.
        
        PERFIL:
        - Nível: {nivel} (iniciante, intermediario, avancado)
        - Objetivo: {objetivo} (perda_peso, ganho_massa, definicao, resistencia)
        - Dias por semana: {dias}
        - Histórico: {historico if historico else "Sem histórico disponível"}
        
        Crie um plano realista e progressivo. Inclua:
        1. Para cada dia da semana, 4-6 exercícios específicos
        2. Séries, repetições e tempo de descanso
        3. Dicas de execução técnica
        4. Aquecimento específico e alongamento
        
        FORMATO DE RESPOSTA (RETORNE APENAS JSON VÁLIDO):
        {{
            "plano": [
                {{
                    "dia": "Dia 1 - Peito e Tríceps",
                    "objetivo": "Hipertrofia de peitoral e tríceps",
                    "exercicios": [
                        {{
                            "nome": "Supino Reto",
                            "series": "4",
                            "repeticoes": "8-12",
                            "descanso": "90 segundos",
                            "dica": "Mantenha as escapulas retraídas e peito elevado"
                        }}
                    ],
                    "aquecimento": "10 minutos de bicicleta + rotação de ombros",
                    "alongamento": "Alongar peitoral 30 segundos cada lado"
                }}
            ],
            "observacoes": "Aumente a carga progressivamente a cada semana"
        }}
        """
        
        try:
            # Configuração otimizada para respostas estruturadas
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json",
            }
            
            print(f"📤 Enviando prompt para Gemini...")
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extrair e processar a resposta
            response_text = response.text
            print(f"📥 Resposta recebida: {len(response_text)} caracteres")
            
            # Extrair JSON da resposta
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Limpar código markdown se presente
                json_str = json_str.replace('```json', '').replace('```', '').strip()
                
                try:
                    result = json.loads(json_str)
                    print(f"✅ Treino gerado com sucesso!")
                    return result
                except json.JSONDecodeError as e:
                    error_msg = f"❌ ERRO ao decodificar JSON: {e}"
                    print(error_msg)
                    raise ValueError(error_msg)
            else:
                error_msg = "❌ Nenhum JSON válido encontrado na resposta da IA"
                print(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"❌ ERRO ao chamar Gemini API: {e}"
            print(error_msg)
            raise ValueError(error_msg)
    
    def criar_dieta_personalizada(self, usuario_data, objetivo, restricoes, preferencias):
        """Cria plano alimentar personalizado com IA (SEMPRE usa IA)"""
        prompt = f"""
        Como nutricionista IA especializado, crie um plano alimentar SEMANAL completo.
        
        DADOS DO USUÁRIO:
        {json.dumps(usuario_data, indent=2)}
        
        OBJETIVO: {objetivo}
        RESTRIÇÕES ALIMENTARES: {restricoes}
        PREFERÊNCIAS ALIMENTARES: {preferencias}
        
        Crie um plano REALISTA, SAUDÁVEL e SUSTENTÁVEL considerando:
        1. Distribuição calórica adequada ao objetivo
        2. Balanceamento de macronutrientes (proteínas, carboidratos, gorduras)
        3. Variedade de alimentos para evitar monotonia
        4. Facilidade de preparo e custo acessível
        
        FORMATO DE RESPOSTA (RETORNE APENAS JSON VÁLIDO):
        {{
            "plano_semanal": {{
                "segunda": {{
                    "cafe_manha": {{
                        "refeicao": "Omelete de 3 ovos com espinafre",
                        "ingredientes": ["3 ovos", "1 xícara de espinafre", "1 colher de azeite"],
                        "calorias": 320,
                        "macros": {{"proteinas": 25, "carboidratos": 3, "gorduras": 23}},
                        "preparo": "Bater os ovos, misturar com espinafre picado e cozinhar em fogo médio"
                    }},
                    "almoco": {{
                        "refeicao": "Peito de frango grelhado com arroz integral e brócolis",
                        "ingredientes": ["150g peito de frango", "1 xícara de arroz integral cozido", "1 xícara de brócolis"],
                        "calorias": 550,
                        "macros": {{"proteinas": 45, "carboidratos": 60, "gorduras": 10}},
                        "preparo": "Grelhar o frango temperado, cozinhar arroz e vaporizar brócolis"
                    }},
                    "lanche": {{...}},
                    "janta": {{...}},
                    "total_diario": {{"calorias": 1850, "proteinas": 140, "carboidratos": 180, "gorduras": 60}}
                }},
                "terca": {{...}},
                "quarta": {{...}},
                "quinta": {{...}},
                "sexta": {{...}},
                "sabado": {{...}},
                "domingo": {{...}}
            }},
            "calorias_diarias": 1850,
            "distribuicao_macros": {{"proteinas": 30, "carboidratos": 40, "gorduras": 30}},
            "lista_compras": [
                {{
                    "categoria": "Proteínas",
                    "itens": [
                        {{"nome": "Peito de frango", "quantidade": "1.5kg", "prioridade": "alta"}},
                        {{"nome": "Ovos", "quantidade": "2 dúzias", "prioridade": "alta"}},
                        {{"nome": "Salmão", "quantidade": "500g", "prioridade": "media"}}
                    ]
                }}
            ],
            "receitas_especiais": [
                {{
                    "nome": "Frango ao Curry Light",
                    "ingredientes": ["500g peito de frango", "1 cebola", "2 dentes de alho", "2 colheres de curry", "1 lata de leite de coco light"],
                    "preparo": "Refogue cebola e alho, adicione frango em cubos, depois curry e leite de coco. Cozinhe por 20min.",
                    "nutricional": {{"porcao": "200g", "calorias": 280, "proteinas": 35, "carboidratos": 8, "gorduras": 12}}
                }}
            ],
            "suplementacao": [
                {{
                    "suplemento": "Whey Protein",
                    "dosagem": "30g pós-treino",
                    "horario": "Imediatamente após o treino",
                    "justificativa": "Para otimizar recuperação muscular"
                }}
            ],
            "recomendacoes_gerais": "Beba 3L de água por dia e mantenha consistência"
        }}
        """
        
        try:
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json",
            }
            
            print(f"📤 Enviando prompt para dieta...")
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            response_text = response.text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                json_str = json_str.replace('```json', '').replace('```', '').strip()
                
                try:
                    result = json.loads(json_str)
                    print(f"✅ Dieta gerada com sucesso!")
                    return result
                except json.JSONDecodeError:
                    error_msg = "❌ ERRO ao decodificar JSON da dieta"
                    print(error_msg)
                    raise ValueError(error_msg)
            else:
                error_msg = "❌ Nenhum JSON válido encontrado na resposta da dieta"
                print(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"❌ ERRO ao gerar dieta: {e}"
            print(error_msg)
            raise ValueError(error_msg)
    
    def analisar_desempenho(self, dados_usuario):
        """Analisa desempenho do usuário com IA (SEMPRE usa IA)"""
        prompt = f"""
        Analise o desempenho do usuário e forneça insights PROFISSIONAIS e DETALHADOS:
        
        DADOS DO USUÁRIO:
        {dados_usuario}
        
        Forneça uma análise COMPLETA em português com:
        
        1. 📈 PROGRESSO GERAL
        - Avaliação do progresso desde o início
        - Comparação com metas estabelecidas
        - Velocidade de progresso (rápido, moderado, lento)
        
        2. ✅ PONTOS FORTES
        - O que está funcionando bem
        - Áreas de melhor desempenho
        - Hábitos positivos consolidados
        
        3. 🔧 ÁREAS PARA MELHORIA
        - Oportunidades de otimização
        - Possíveis gargalos no progresso
        - Comportamentos a ajustar
        
        4. 🎯 RECOMENDAÇÕES ESPECÍFICAS
        - Ajustes no treino (se aplicável)
        - Ajustes na dieta (se aplicável)
        - Mudanças na rotina ou recuperação
        
        5. 🏆 META PARA PRÓXIMA SEMANA
        - Objetivo específico e mensurável
        - Ações concretas para alcançar
        - Métricas para acompanhar
        
        6. 💪 MOTIVAÇÃO
        - Mensagem encorajadora personalizada
        - Lembrete dos benefícios alcançados
        - Perspectiva para o futuro
        
        Formate a resposta em parágrafos claros e organizados, usando emojis para melhor visualização.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = f"❌ ERRO na análise de desempenho: {e}"
            print(error_msg)
            raise ValueError(error_msg)