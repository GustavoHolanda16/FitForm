import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no .env")
        
        genai.configure(api_key=api_key)
        # ✅ CORRIGIDO: Usar modelo atualizado
        # Opção 1 (Recomendada): Modelo estável mais recente
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        # Opção 2 (Alternativa): Modelo experimental mais recente
        # self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def gerar_treino_ia(self, nivel, objetivo, dias, historico=""):
        prompt = f"""
        Como personal trainer IA, gere um plano de treino personalizado.
        
        PERFIL:
        - Nível: {nivel}
        - Objetivo: {objetivo}
        - Dias por semana: {dias}
        - Histórico: {historico if historico else "Sem histórico disponível"}
        
        FORMATO DE RESPOSTA:
        1. Para cada dia, liste 4-6 exercícios
        2. Inclua séries, repetições e descanso
        3. Adicione dicas de execução
        4. Inclua recomendações de aquecimento e alongamento
        
        Retorne em formato JSON:
        {{
            "plano": [
                {{
                    "dia": "Dia 1",
                    "objetivo": "string",
                    "exercicios": [
                        {{
                            "nome": "string",
                            "series": "string",
                            "repeticoes": "string",
                            "descanso": "string",
                            "dica": "string"
                        }}
                    ],
                    "aquecimento": "string",
                    "alongamento": "string"
                }}
            ],
            "observacoes": "string"
        }}
        """
        
        try:
            # ✅ ADICIONAR: Configuração para resposta JSON
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return self._parse_response(response.text)
        except Exception as e:
            print(f"Erro Gemini: {e}")
            return self._get_fallback_treino(nivel, objetivo, dias)
    
    def _parse_response(self, response_text):
        # Melhorado: parsing mais robusto
        import json
        import re
        
        try:
            # Tenta encontrar JSON na resposta
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response_text, re.DOTALL)
            
            if match:
                json_str = match.group(0)
                # Limpar possíveis markdown
                json_str = json_str.replace('```json', '').replace('```', '')
                return json.loads(json_str.strip())
            else:
                # Se não encontrar JSON, retorna fallback
                return self._get_fallback_response()
                
        except json.JSONDecodeError as e:
            print(f"Erro ao parsear JSON: {e}")
            return self._get_fallback_response()
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self):
        """Resposta de fallback padrão"""
        return {
            "plano": [],
            "observacoes": "Resposta da IA não pôde ser processada. Use o gerador manual."
        }
    
    def _get_fallback_treino(self, nivel, objetivo, dias):
        """Fallback baseado em lógica local"""
        # Verifica se a função existe localmente
        try:
            from .utils import gerar_treino_personalizado
            treino = gerar_treino_personalizado(nivel, objetivo, dias)
            return {
                "plano": treino,
                "observacoes": "Plano gerado pelo sistema base (fallback)"
            }
        except ImportError:
            # Fallback básico se o módulo utils não existir
            plano_basico = [
                {
                    "dia": "Dia 1 - Full Body",
                    "objetivo": "Treino básico para iniciantes",
                    "exercicios": [
                        {
                            "nome": "Agachamento",
                            "series": "3",
                            "repeticoes": "10-12",
                            "descanso": "60s",
                            "dica": "Mantenha as costas retas"
                        },
                        {
                            "nome": "Flexão de braço",
                            "series": "3",
                            "repeticoes": "8-10",
                            "descanso": "60s",
                            "dica": "Mantenha o corpo alinhado"
                        }
                    ],
                    "aquecimento": "5 min de bicicleta + alongamentos dinâmicos",
                    "alongamento": "Alongamentos estáticos por 30s cada músculo"
                }
            ]
            return {
                "plano": plano_basico,
                "observacoes": "Plano básico - IA indisponível"
            }
    
    def analisar_desempenho(self, dados_usuario):
        prompt = f"""
        Analise o desempenho do usuário e forneça insights:
        
        DADOS:
        {dados_usuario}
        
        Forneça:
        1. Progresso geral
        2. Pontos fortes
        3. Áreas para melhoria
        4. Recomendações específicas
        5. Meta para próxima semana
        
        Formate a resposta em parágrafos claros.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Não foi possível analisar os dados no momento. Erro: {str(e)}"