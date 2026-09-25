#1- IMPORTS
from persistencia import carregar_dados, salvar_dados
from sistema_financeiro import SistemaFinanceiro



#2- FUNÇÕES
def mostrar_menu():
    print('GESTÃO FINANCEIRA')
    print()
    print('1 - Registrar receita')
    print('2 - Registrar despesa')
    print('3 - Consultar saldo')
    print('4 - Resumo financeiro')
    print('5 - Histórico financeiro')
    print('6 - Sair')
    


#3- DADOS
dados = carregar_dados()

receitas = dados['receitas']
despesas = dados['despesas']

sistema = SistemaFinanceiro(receitas, despesas)



#4- PROGRAMA PRINCIPAL
while True:    
    mostrar_menu()
    opcao = input('Escolha uma opção: ')
    
    if opcao == '1':
        sistema.registrar_receita()
        salvar_dados(receitas, despesas)
    
    elif opcao == '2':
        sistema.registrar_despesa()
        salvar_dados(receitas, despesas)
        
    elif opcao == '3':
        sistema.mostrar_saldo()
        
    elif opcao == '4':
        sistema.mostrar_resumo()

    elif opcao == '5':
        sistema.mostrar_historico()
    
    elif opcao == '6':
        break
    
    else:
        print('Opção inválida!')
    
    
    
    