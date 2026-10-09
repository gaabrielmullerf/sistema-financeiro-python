"""Validação financeira e apresentação do menu, sem SQL."""

from decimal import Decimal, InvalidOperation


def validar_descricao(descricao):
    if not isinstance(descricao, str):
        raise ValueError('A descrição deve ser um texto.')
    descricao = descricao.strip()
    if not descricao or len(descricao) > 150 or '\x00' in descricao:
        raise ValueError('A descrição deve ter entre 1 e 150 caracteres, sem caractere nulo.')
    return descricao


def validar_valor(entrada):
    """Não arredonda silenciosamente valores com frações de centavo."""
    if not isinstance(entrada, (str, Decimal, int)) or isinstance(entrada, bool):
        raise ValueError('Informe um valor decimal, sem usar float.')
    texto = str(entrada).strip().replace(',', '.')
    try:
        valor = Decimal(texto)
        if not valor.is_finite() or valor <= 0 or valor > Decimal('9999999999.99'):
            raise ValueError('O valor deve ser positivo e no máximo 9999999999,99.')
        centavos = valor.quantize(Decimal('0.01'))
        if valor != centavos:
            raise ValueError('Use no máximo duas casas decimais; o valor não será arredondado.')
        return centavos
    except InvalidOperation as erro:
        raise ValueError('Valor inválido. Use números, como 125,50, sem separador de milhares.') from erro


class SistemaFinanceiro:
    def __init__(self, persistencia):
        self.persistencia = persistencia

    def calcular_totais(self):
        return self.persistencia.calcular_totais()

    def _registrar(self, tipo):
        descricao = input(f'Qual o tipo da {tipo}? ')
        entrada = input(f'Qual o valor da {tipo}? ')
        try:
            descricao = validar_descricao(descricao)
            valor = validar_valor(entrada)
        except ValueError as erro:
            print(erro)
            return
        if tipo == 'receita':
            self.persistencia.registrar_receita(descricao, valor)
        else:
            self.persistencia.registrar_despesa(descricao, valor)
        # Só informa sucesso após o commit realizado pela persistência.
        print(f'{tipo.capitalize()} registrada com sucesso!')
        print(f'Descrição: {descricao}.')
        print(f'Valor: R$ {valor:.2f}.')

    def registrar_receita(self):
        self._registrar('receita')

    def registrar_despesa(self):
        self._registrar('despesa')

    def mostrar_saldo(self):
        receitas, despesas = self.calcular_totais()
        print('======== SALDO ========')
        print(f'Saldo: R$ {receitas - despesas:.2f}')

    def mostrar_resumo(self):
        receitas, despesas = self.calcular_totais()
        print('====== RESUMO FINANCEIRO ======')
        print(f'Total de receitas: R$ {receitas:.2f}')
        print(f'Total de despesas: R$ {despesas:.2f}')
        print(f'Resultado: R$ {receitas - despesas:.2f}')

    def mostrar_historico(self):
        receitas, despesas = self.persistencia.carregar_historico()
        print('======== RECEITAS ========')
        self._mostrar_movimentacoes(receitas, 'Nenhuma receita registrada.')
        print('======== DESPESAS ========')
        self._mostrar_movimentacoes(despesas, 'Nenhuma despesa registrada.')

    @staticmethod
    def _mostrar_movimentacoes(movimentacoes, mensagem_vazia):
        if not movimentacoes:
            print(mensagem_vazia)
        for item in movimentacoes:
            print(f"{item['descricao']} - R$ {item['valor']:.2f}")
