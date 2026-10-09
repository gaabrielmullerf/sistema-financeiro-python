import io
import json
from contextlib import redirect_stdout
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from migrar_json import ler_legado
from persistencia import ErroPersistencia
from sistema_financeiro import SistemaFinanceiro, validar_descricao, validar_valor


class ValidacoesTest(unittest.TestCase):
    def test_valores_validos_sem_perda_de_precisao(self):
        for entrada, esperado in [('0,10', '0.10'), ('125.50', '125.50'), ('9999999999.99', '9999999999.99'), ('1.000', '1.00')]:
            with self.subTest(entrada=entrada):
                self.assertEqual(validar_valor(entrada), Decimal(esperado))
        self.assertEqual(validar_valor('0.1') + validar_valor('0.2'), Decimal('0.30'))

    def test_valores_invalidos(self):
        for entrada in ['0', '-1', 'abc', '', 'NaN', 'Infinity', '-Infinity', '1.001', '10000000000', '1.234,56', True, 1.2, None, '1e999999']:
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                validar_valor(entrada)

    def test_descricao(self):
        self.assertEqual(validar_descricao('  Serviços  '), 'Serviços')
        for entrada in ['', '   ', 'x' * 151, '\x00', 123]:
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                validar_descricao(entrada)


class MenuTest(unittest.TestCase):
    def setUp(self):
        self.repo = Mock()
        self.sistema = SistemaFinanceiro(self.repo)

    def test_receita_usa_decimal_e_imprime_sucesso(self):
        with patch('builtins.input', side_effect=['Serviço', '10,25']), redirect_stdout(io.StringIO()) as saida:
            self.sistema.registrar_receita()
        self.repo.registrar_receita.assert_called_once_with('Serviço', Decimal('10.25'))
        self.assertIn('Receita registrada com sucesso!', saida.getvalue())

    def test_valor_invalido_nao_grava(self):
        with patch('builtins.input', side_effect=['Serviço', '-10']), redirect_stdout(io.StringIO()):
            self.sistema.registrar_receita()
        self.repo.registrar_receita.assert_not_called()

    def test_falha_nao_anuncia_sucesso(self):
        self.repo.registrar_despesa.side_effect = ErroPersistencia('Falha')
        with patch('builtins.input', side_effect=['Aluguel', '10']), redirect_stdout(io.StringIO()) as saida:
            with self.assertRaises(ErroPersistencia):
                self.sistema.registrar_despesa()
        self.assertNotIn('sucesso', saida.getvalue())

    def test_saldo_e_resumo(self):
        self.repo.calcular_totais.return_value = (Decimal('1000.10'), Decimal('250.20'))
        with redirect_stdout(io.StringIO()) as saida:
            self.sistema.mostrar_saldo()
            self.sistema.mostrar_resumo()
        self.assertIn('Saldo: R$ 749.90', saida.getvalue())
        self.assertIn('Resultado: R$ 749.90', saida.getvalue())

    def test_historico_vazio(self):
        self.repo.carregar_historico.return_value = ([], [])
        with redirect_stdout(io.StringIO()) as saida:
            self.sistema.mostrar_historico()
        self.assertIn('Nenhuma receita registrada.', saida.getvalue())
        self.assertIn('Nenhuma despesa registrada.', saida.getvalue())

    def test_main_trata_indisponibilidade(self):
        import main
        with patch('main.PersistenciaPostgres') as classe, redirect_stdout(io.StringIO()) as saida:
            classe.return_value.verificar_estrutura.side_effect = ErroPersistencia('Banco indisponível')
            self.assertEqual(main.main(), 1)
        self.assertIn('Banco indisponível', saida.getvalue())

    def test_main_permite_continuar_apos_falha(self):
        import main
        with patch('main.PersistenciaPostgres') as classe, patch('builtins.input', side_effect=['3', '6']), redirect_stdout(io.StringIO()) as saida:
            classe.return_value.calcular_totais.side_effect = ErroPersistencia('Falha de consulta')
            self.assertEqual(main.main(), 0)
        self.assertIn('Falha de consulta', saida.getvalue())


class LegadoTest(unittest.TestCase):
    def test_leitura_preserva_json_e_decimal(self):
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / 'dados.json'
            original = '{"receitas": [{"descricao": "Serviço", "valor": 0.10}], "despesas": []}'
            arquivo.write_text(original, encoding='utf-8')
            dados, resumo = ler_legado(arquivo)
            self.assertEqual(dados['receitas'], [('Serviço', Decimal('0.10'))])
            self.assertEqual(len(resumo), 64)
            self.assertEqual(arquivo.read_text(encoding='utf-8'), original)

    def test_rejeita_arquivo_invalido_ou_vazio(self):
        casos = [{}, {'receitas': [], 'despesas': []}, {'receitas': [{'descricao': 'A', 'valor': -1}], 'despesas': []}, {'receitas': 'erro', 'despesas': []}]
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / 'dados.json'
            for caso in casos:
                arquivo.write_text(json.dumps(caso), encoding='utf-8')
                with self.subTest(caso=caso), self.assertRaises(ValueError):
                    ler_legado(arquivo)


if __name__ == '__main__':
    unittest.main()
