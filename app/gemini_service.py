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
        self.model = genai.GenerativeModel('gemini-pro')
    
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
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            print(f"Erro Gemini: {e}")
            return self._get_fallback_treino(nivel, objetivo, dias)
    
    def _parse_response(self, response_text):
        # Simplificado - em produção, use JSON parsing robusto
        import json
        try:
            # Extrai JSON da resposta
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            return json.loads(json_str)
        except:
            # Fallback se não conseguir parsear
            return {"plano": [], "observacoes": "Erro ao processar resposta da IA"}
    
    def _get_fallback_treino(self, nivel, objetivo, dias):
        from .utils import gerar_treino_personalizado
        treino = gerar_treino_personalizado(nivel, objetivo, dias)
        return {
            "plano": treino,
            "observacoes": "Plano gerado pelo sistema base (fallback)"
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
        """
        
        response = self.model.generate_content(prompt)
        return response.text