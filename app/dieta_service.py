import json
from .gemini_service import GeminiService

class DietaService:
    def __init__(self):
        # Inicializa o serviço Gemini - SE FALHAR, lança exceção
        self.gemini = GeminiService()
    
    def criar_dieta_personalizada(self, usuario_data, objetivo, restricoes, preferencias):
        """
        Cria plano alimentar personalizado SEMPRE usando IA
        """
        try:
            print(f"🍎 Criando dieta personalizada para {usuario_data.get('nome', 'usuário')}")
            print(f"   Objetivo: {objetivo}")
            print(f"   Restrições: {restricoes}")
            print(f"   Preferências: {preferencias}")
            
            # Usa o método diretamente do GeminiService
            dieta = self.gemini.criar_dieta_personalizada(
                usuario_data, 
                objetivo, 
                restricoes, 
                preferencias
            )
            
            print(f"✅ Dieta criada com sucesso!")
            return dieta
            
        except Exception as e:
            error_msg = f"❌ ERRO CRÍTICO: Falha ao criar dieta com IA: {e}"
            print(error_msg)
            raise ValueError(error_msg)
    
    def ajustar_dieta(self, dieta_atual, feedback, progresso):
        """Ajusta dieta baseada no feedback e progresso SEMPRE usando IA"""
        try:
            prompt = f"""
            Ajuste o plano alimentar baseado no feedback do usuário:
            
            DIETA ATUAL:
            {json.dumps(dieta_atual, indent=2)}
            
            FEEDBACK DO USUÁRIO: {feedback}
            PROGRESSO ATUAL: {progresso}
            
            Faça os seguintes ajustes considerando:
            1. 🍽️ SACIEDADE: O usuário está satisfeito com as porções?
            2. 📊 RESULTADOS: O progresso está adequado para os objetivos?
            3. ♻️ SUSTENTABILIDADE: A dieta é fácil de manter a longo prazo?
            4. 🌈 VARIEDADE: Há diversidade suficiente nos alimentos?
            5. ⏰ PRATICIDADE: As refeições são fáceis de preparar?
            6. 💰 CUSTO: Os ingredientes são financeiramente acessíveis?
            
            Retorne a dieta AJUSTADA no mesmo formato JSON, com as modificações claramente explicadas.
            
            FORMATO:
            {{
                "dieta_ajustada": {{...}},
                "alteracoes_realizadas": [
                    "Mudança 1: Descrição...",
                    "Mudança 2: Descrição..."
                ],
                "justificativa": "Explicação das mudanças..."
            }}
            """
            
            # Usar o modelo Gemini diretamente
            response = self.gemini.model.generate_content(prompt)
            
            # Extrair JSON da resposta
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                json_str = json_str.replace('```json', '').replace('```', '').strip()
                resultado = json.loads(json_str)
                
                # Retorna a dieta ajustada
                if "dieta_ajustada" in resultado:
                    print(f"✅ Dieta ajustada com sucesso!")
                    return resultado["dieta_ajustada"]
                else:
                    print(f"⚠️  Aviso: Formato de resposta inesperado")
                    return resultado
            
            error_msg = "❌ Resposta da IA não contém JSON válido"
            print(error_msg)
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = f"❌ ERRO ao ajustar dieta com IA: {e}"
            print(error_msg)
            raise ValueError(error_msg)