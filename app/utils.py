from .gemini_service import GeminiService

def gerar_treino_personalizado(nivel, objetivo, dias, usar_ia=True, historico=""):
    """
    Gera treino personalizado, com opção de usar IA
    """
    if usar_ia:
        try:
            gemini = GeminiService()
            return gemini.gerar_treino_ia(nivel, objetivo, dias, historico)
        except Exception as e:
            print(f"Falha na IA, usando sistema base: {e}")
    
    # Sistema base (existente)
    return _gerar_treino_base(nivel, objetivo, dias)

def _gerar_treino_base(nivel, objetivo, dias):
    # Move o código original para cá
    treinos = {
        # ... código existente do dicionário treinos
    }
    # ... resto do código existente