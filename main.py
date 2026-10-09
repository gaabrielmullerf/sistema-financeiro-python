"""Ponto de entrada da aplicação de terminal."""

from persistencia import ErroPersistencia, PersistenciaPostgres
from sistema_financeiro import SistemaFinanceiro


def mostrar_menu():
    print('\nGESTÃO FINANCEIRA\n')
    print('1 - Registrar receita')
    print('2 - Registrar despesa')
    print('3 - Consultar saldo')
    print('4 - Resumo financeiro')
    print('5 - Histórico financeiro')
    print('6 - Sair')


def main():
    persistencia = PersistenciaPostgres()
    try:
        persistencia.verificar_estrutura()
    except ErroPersistencia as erro:
        print(erro)
        return 1

    sistema = SistemaFinanceiro(persistencia)
    acoes = {
        '1': sistema.registrar_receita,
        '2': sistema.registrar_despesa,
        '3': sistema.mostrar_saldo,
        '4': sistema.mostrar_resumo,
        '5': sistema.mostrar_historico,
    }
    try:
        while True:
            mostrar_menu()
            opcao = input('Escolha uma opção: ').strip()
            if opcao == '6':
                return 0
            acao = acoes.get(opcao)
            if acao is None:
                print('Opção inválida!')
                continue
            try:
                acao()
            except ErroPersistencia as erro:
                print(erro)
    except (EOFError, KeyboardInterrupt):
        print('\nPrograma encerrado.')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
