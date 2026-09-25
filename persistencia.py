import json

def salvar_dados(receitas, despesas):
    dados = {
        'receitas': receitas,
        'despesas': despesas
    }
    
    with open('dados.json', 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)

def carregar_dados():
    try:
        with open('dados.json', 'r') as arquivo:
            dados = json.load(arquivo)
            return dados
            
    except FileNotFoundError:
        return {
            'receitas': [],
            'despesas': []
        }
        
    except  json.JSONDecodeError:
        return {
            'receitas': [],
            'despesas': []
        }
