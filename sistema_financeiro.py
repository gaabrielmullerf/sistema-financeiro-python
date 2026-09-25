class SistemaFinanceiro:
    
    def __init__(self, receitas, despesas):
        self.receitas = receitas
        self.despesas = despesas
        
    
    
    def calcular_totais(self):
        total_receitas = 0
        total_despesas = 0
        
        for receita in self.receitas:
            total_receitas += receita['valor']
            
        for despesa in self.despesas:
            total_despesas += despesa['valor']
            
        return total_receitas, total_despesas    
        
    
    
    def registrar_receita(self):
        descricao = input('Qual o tipo da receita? ')
        
        try:
            valor_receita = float(input('Qual o valor da receita? '))
        except ValueError:
            print('Valor inválido! Digite apenas números.')
            return
        
        if valor_receita > 0:
            receita = {
                'descricao': descricao,
                'valor': valor_receita
            }
            
            self.receitas.append(receita) #append add elemento ao final da lista
            
            print('Receita registrada com sucesso! ')
            print(f'Descrição: {descricao}.')
            print(f'Valor: R$ {valor_receita:.2f}.')
            
        else:
            print('Valor inválido!')

    
    
    def registrar_despesa(self):
        descricao = input('Qual o tipo de despesa? ')
        
        try:
            valor_despesa = float(input('Qual o valor da despesa? '))
        except ValueError:
            print('Valor inválido! Digite apenas números.')
            return
        
        if valor_despesa > 0:
            despesa = {
                'descricao' : descricao,
                'valor' : valor_despesa
            }
            
            self.despesas.append(despesa)
            
            print('Despesa registrada com sucesso!')
            print(f'Descrição: {descricao}.')
            print(f'Valor: R$ {valor_despesa:.2f}.')
        
        else:
            print('Valor inválido!')
  
    
    
    def mostrar_saldo(self):
        total_receitas, total_despesas = self.calcular_totais()
        
        saldo = total_receitas - total_despesas
    
        print('======== SALDO ========')
        print(f'Saldo: R$ {saldo:.2f}')
    
    
    
    def mostrar_historico(self):
        
        print('======== RECEITAS ========')
        if self.receitas:
            for receita in self.receitas:
                print(f"{receita['descricao']} - R$ {receita['valor']:.2f}")
        
        else:
            print('Nenhuma receita registrada.')
            
        print('======== DESPESAS ========')
        if self.despesas:
            for despesa in self.despesas:
                print(f"{despesa['descricao']} - R$ {despesa['valor']:.2f}")
                
        else:
            print('Nenhuma despesa registrada.')
        
        
        
    def mostrar_resumo(self):
        total_receitas, total_despesas = self.calcular_totais()
        
        print('====== RESUMO FINANCEIRO ======')
        print()
        print(f'Total de receitas: R$ {total_receitas:.2f}')
        print(f'Total de despesas: R$ {total_despesas:.2f}')
        print(f'Resultado: R$ {total_receitas - total_despesas:.2f}')
        
        
        