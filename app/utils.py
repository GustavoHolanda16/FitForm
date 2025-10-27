def gerar_treino_personalizado(nivel,objetivo,dias):
    treinos = {
        '1' : { #Básico
            '1' : { #Hipertfia
                'A': ["Agachamento livre", "Supino reto", "Remada baixa", "Abdominal tradicional"],
                'B': ["Leg press", "Desenvolvimento com halteres", "Rosca direta", "Prancha 30s"],
                'C': ["Cadeira extensora", "Tríceps pulley", "Flexão de braço", "Abdominal infra"]
            },
            '2': {  # Perda de peso
                'A': ["Caminhada rápida 30min", "Agachamento leve", "Flexão", "Prancha 30s"],
                'B': ["Bicicleta ergométrica 25min", "Corrida leve 15min", "Abdominal curto", "Alongamento geral"],
                'C': ["Circuito leve (3x): Polichinelo, Agachamento, Corrida parada, Flexão"]
            },
            '3': {  # Condicionamento físico
                'A': ["Corrida leve 2km", "Polichinelos", "Abdominal prancha", "Agachamento"],
                'B': ["Subida de escada 10min", "Corrida estacionária", "Prancha 40s", "Abdominal oblíquo"],
                'C': ["Circuito básico: 3 voltas de 10 flexões, 20 agachamentos, 20 abdominais"]
            }
        },

        '2': {  # INTERMEDIÁRIO
            '1': {
                'A': ["Agachamento livre", "Supino inclinado", "Puxada frontal", "Abdômen prancha 45s"],
                'B': ["Stiff", "Desenvolvimento militar", "Rosca direta", "Tríceps testa"],
                'C': ["Leg press", "Crucifixo reto", "Remada curvada", "Abdominal infra"],
                'D': ["Afundo", "Flexão diamante", "Rosca alternada", "Prancha lateral"],
                'E': ["Cadeira extensora", "Tríceps corda", "Corrida leve 20min", "Alongamento geral"]
            },
            '2': {
                'A': ["Esteira 20min + Circuito: Agachamento, Prancha, Flexão"],
                'B': ["Corrida + Musculação: Stiff, Supino, Abdominal"],
                'C': ["HIIT leve: 30s on/30s off (Burpee, Agachamento, Corrida parada)"],
                'D': ["Treino funcional: Escada, Prancha, Polichinelo, Agachamento"],
                'E': ["Alongamento e corrida leve 15min + Core (Abdominal e prancha)"]
            },
            '3': {
                'A': ["Corrida 3km", "Agachamento com salto", "Flexões rápidas", "Abdominal prancha 1min"],
                'B': ["Burpees", "Corrida estacionária", "Prancha dinâmica", "Abdominal lateral"],
                'C': ["HIIT (20min): Corrida, Polichinelo, Flexão, Agachamento"],
                'D': ["Corrida 2km + Circuito funcional", "Flexão diamante", "Abdominal infra"],
                'E': ["Simulação TAF: Barra, Corrida 12min, Prancha 1min"]
            }
        },

        '3': {  # AVANÇADO
            '1': {
                'A': ["Agachamento livre pesado", "Supino reto pesado", "Remada curvada", "Abdômen com carga"],
                'B': ["Terra", "Desenvolvimento com barra", "Rosca direta", "Prancha com peso"],
                'C': ["Leg press pesado", "Crucifixo inclinado", "Tríceps francês", "Abdominal infra com elevação"],
                'D': ["Agachamento frontal", "Flexão diamante", "Remada unilateral", "Prancha 1min"],
                'E': ["Exercícios compostos e corrida 3km"]
            },
            '2': {
                'A': ["Corrida 4km + Circuito pesado", "Agachamento com salto", "Burpees", "Abdominal prancha 1min"],
                'B': ["HIIT 25min: Sprint, Polichinelo, Flexão, Corrida estacionária"],
                'C': ["Treino funcional militar", "Flexões rápidas", "Prancha lateral com carga"],
                'D': ["Barra fixa", "Corrida intervalada 100m", "Escalada no solo"],
                'E': ["Simulação TAF completa + alongamento"]
            },
            '3': {
                'A': ["HIIT Militar", "Corrida 5km", "Flexões com peso", "Abdômen completo"],
                'B': ["Sprint + Burpee + Prancha", "Corrida intervalada 400m", "Flexões rápidas"],
                'C': ["Circuito tático: Barra, Corrida, Flexão, Prancha"],
                'D': ["Simulação TAF", "Corrida cronometrada", "Prancha de resistência"],
                'E': ["Condicionamento total: 10km + 50 flexões + 100 abdominais"]
            }
        }
    }

    plano = treinos.get(nivel, {}).get(objetivo, {})

    dias_treino = int(dias)
    treino_semana = []
    dias_disponiveis = list(plano.keys())[:dias_treino]

    for dia in dias_disponiveis:
        treino_semana.append({
            'dia': f'Treino {dia}',
            'exercicios': plano[dia]
        })

    return treino_semana