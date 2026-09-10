#1- IMPORTS
import json

#2- FUNÇÕES
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

def calcular_totais(receitas, despesas):
    total_receitas = 0
    total_despesas = 0
    
    for receita in receitas:
        total_receitas += receita['valor']
    
    for despesa in despesas:
        total_despesas += despesa['valor']
        
    return total_receitas, total_despesas    

def mostrar_menu():
    print('GESTÃO FINANCEIRA')
    print()
    print('1 - Registrar receita')
    print('2 - Registrar despesa')
    print('3 - Consultar saldo')
    print('4 - Resumo financeiro')
    print('5 - Histórico financeiro')
    print('6 - Sair')
    

def registrar_receita(total_receitas, receitas):
    descricao = input('Qual o tipo de receita? ')
    try: 
        valor_receita = float(input('Qual o valor da receita? '))
    except ValueError:
        print('Valor inválido! Digite apenas números.')
        return total_receitas
    
    if valor_receita > 0:
        total_receitas += valor_receita
        receita = {
            'descricao' : descricao,
            'valor' : valor_receita
        }
        receitas.append(receita)
        print('Receita registrada com sucesso!')
        print(f'Descrição: {descricao}.')
        print(f'Valor: R$ {valor_receita:.2f}.')   
        return total_receitas
        
    else:
        print('Valor inválido!')
        return total_receitas
        
        
def registrar_despesa(total_despesas, despesas):
    descricao = input('Qual o tipo de despesa? ')
    try:
        valor_despesa = float(input('Qual o valor da despesa? '))
    except ValueError:
        print('Valor inválido! Digite apenas números.')
        return total_despesas
        
    if valor_despesa > 0:
        total_despesas += valor_despesa
        despesa = {
            'descricao' : descricao,
            'valor' : valor_despesa
        }
        despesas.append(despesa)
        print('Despesa registrada com sucesso!')
        print(f'Descrição: {descricao}.')
        print(f'Valor: R$ {valor_despesa:.2f}.')
        return total_despesas
        
    else:
        print('Valor inválido!')
        return total_despesas
        
def mostrar_saldo(total_receitas, total_despesas):
    saldo = total_receitas - total_despesas
    print('======== SALDO ========')
    print(f'Saldo: R$ {saldo:.2f}')
    
def mostrar_historico(receitas, despesas):
    print('======== RECEITAS ========')
    if receitas:
        for receita in receitas:
            print(f"{receita['descricao']} - R$ {receita['valor']:.2f}")
    else:
        print('Nenhuma receita registrada.')
    
    print('======== DESPESAS ========')
    if despesas:
        for despesa in despesas:
            print(f"{despesa['descricao']} - R$ {despesa['valor']:.2f}")
    else:
        print('Nenhuma despesa registrada.')

def mostrar_resumo(total_receitas, total_despesas):
    print('====== RESUMO FINANCEIRO ======')
    print()
    print(f'Total de receitas: R$ {total_receitas:.2f}')
    print(f'Total de despesas: R$ {total_despesas:.2f}')
    print(f'Resultado: R$ {total_receitas - total_despesas:.2f}')
    
#3- DADOS
dados = carregar_dados()

receitas = dados['receitas']
despesas = dados['despesas']

total_receitas, total_despesas = calcular_totais(receitas, despesas)

#4- PROGRAMA PRINCIPAL
while True:    
    mostrar_menu()
    opcao = input('Escolha uma opção: ')
    
    if opcao == '1':
        total_receitas = registrar_receita(total_receitas, receitas)
        salvar_dados(receitas, despesas)
    
    elif opcao == '2':
        total_despesas = registrar_despesa(total_despesas, despesas)
        salvar_dados(receitas, despesas)
        
    elif opcao == '3':
        mostrar_saldo(total_receitas, total_despesas)
        
    elif opcao == '4':
        mostrar_resumo(total_receitas, total_despesas)

    elif opcao == '5':
        mostrar_historico(receitas, despesas)
    
    elif opcao == '6':
        break
    
    else:
        print('Opção inválida!')
    
    
    
    