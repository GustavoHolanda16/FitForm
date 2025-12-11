import json
from .gemini_service import GeminiService

class DietaService:
    def __init__(self):
        self.gemini = GeminiService()
    
    def criar_dieta_personalizada(self, usuario_data, objetivo, restricoes, preferencias):
        """
        Cria plano alimentar personalizado
        """
        prompt = f"""
        Como nutricionista IA, crie um plano alimentar completo:
        
        DADOS DO USUÁRIO:
        {json.dumps(usuario_data, indent=2)}
        
        OBJETIVO: {objetivo}
        RESTRIÇÕES: {restricoes}
        PREFERÊNCIAS: {preferencias}
        
        FORMATO DE RESPOSTA JSON:
        {{
            "plano_semanal": {{
                "segunda": {{
                    "cafe_manha": {{
                        "refeicao": "string",
                        "ingredientes": ["ing1", "ing2"],
                        "calorias": number,
                        "macros": {{"proteinas": number, "carboidratos": number, "gorduras": number}},
                        "preparo": "string"
                    }},
                    "almoco": {{...}},
                    "lanche": {{...}},
                    "janta": {{...}},
                    "total_diario": {{"calorias": number, "proteinas": number, "carboidratos": number, "gorduras": number}}
                }}
            }},
            "calorias_diarias": number,
            "distribuicao_macros": {{"proteinas": number, "carboidratos": number, "gorduras": number}},
            "lista_compras": [
                {{
                    "categoria": "Proteínas",
                    "itens": [
                        {{"nome": "string", "quantidade": "string", "prioridade": "alta/media/baixa"}}
                    ]
                }}
            ],
            "receitas_especiais": [
                {{
                    "nome": "string",
                    "ingredientes": ["string"],
                    "preparo": "string",
                    "nutricional": {{...}}
                }}
            ],
            "suplementacao": [
                {{
                    "suplemento": "string",
                    "dosagem": "string",
                    "horario": "string",
                    "justificativa": "string"
                }}
            ]
        }}
        """
        
        response = self.gemini.model.generate_content(prompt)
        return self._parse_dieta_response(response.text)
    
    def ajustar_dieta(self, dieta_atual, feedback, progresso):
        """Ajusta dieta baseado no feedback e progresso"""
        prompt = f"""
        Ajuste o plano alimentar baseado no feedback:
        
        DIETA ATUAL:
        {json.dumps(dieta_atual, indent=2)}
        
        FEEDBACK DO USUÁRIO: {feedback}
        PROGRESSO: {progresso}
        
        Faça ajustes considerando:
        1. Saciedade do usuário
        2. Resultados obtidos
        3. Sustentabilidade
        4. Variedade
        """
        
        response = self.gemini.model.generate_content(prompt)
        return self._parse_ajuste_response(response.text)