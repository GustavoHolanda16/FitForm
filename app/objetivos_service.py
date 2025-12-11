import json
from datetime import datetime, timedelta
from .gemini_service import GeminiService

class ObjetivoService:
    def __init__(self):
        self.gemini = GeminiService()
    
    def criar_objetivo_personalizado(self, usuario_data, objetivo_tipo, prazo_semanas):
        """
        Cria um objetivo SMART (Específico, Mensurável, Atingível, Relevante, Temporal)
        """
        prompt = f"""
        Crie um objetivo fitness SMART para o usuário:
        
        DADOS DO USUÁRIO:
        {json.dumps(usuario_data, indent=2)}
        
        TIPO DE OBJETIVO: {objetivo_tipo}
        PRAZO: {prazo_semanas} semanas
        
        FORMATO DE RESPOSTA JSON:
        {{
            "titulo": "Título motivacional",
            "descricao": "Descrição detalhada",
            "tipo": "{objetivo_tipo}",
            "prazo_semanas": {prazo_semanas},
            "data_inicio": "YYYY-MM-DD",
            "data_fim": "YYYY-MM-DD",
            "metas_semanais": [
                {{
                    "semana": 1,
                    "descricao": "Meta para a semana 1",
                    "indicadores": ["indicador1", "indicador2"],
                    "treinos_recomendados": ["tipo1", "tipo2"]
                }}
            ],
            "kpis": {{
                "principal": "ex: peso_kg",
                "secundarios": ["imc", "percentual_gordura", "circunferencias"]
            }},
            "checkpoints": [
                {{
                    "semana": 4,
                    "descricao": "Primeira avaliação",
                    "metrica_esperada": "ex: -2kg"
                }}
            ],
            "motivacao": "Frase motivacional personalizada",
            "dicas_psicologicas": ["dica1", "dica2"]
        }}
        """
        
        try:
            response = self.gemini.model.generate_content(prompt)
            return self._parse_objetivo_response(response.text, prazo_semanas)
        except Exception as e:
            return self._criar_objetivo_base(usuario_data, objetivo_tipo, prazo_semanas)
    
    def acompanhar_progresso(self, objetivo, progresso_atual):
        """Analisa progresso em relação ao objetivo"""
        prompt = f"""
        Analise o progresso do usuário em relação ao objetivo:
        
        OBJETIVO:
        {json.dumps(objetivo, indent=2)}
        
        PROGRESSO ATUAL:
        {json.dumps(progresso_atual, indent=2)}
        
        Forneça:
        1. Percentual de conclusão
        2. Pontos positivos
        3. Alertas/riscos
        4. Ajustes recomendados
        5. Motivação baseada no progresso
        
        Formato JSON.
        """
        
        response = self.gemini.model.generate_content(prompt)
        return self._parse_progresso_response(response.text)