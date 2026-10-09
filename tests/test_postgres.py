"""Integração opt-in. Cria e remove somente schemas temporários próprios."""

from decimal import Decimal
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4

import psycopg
from psycopg import sql
from dotenv import load_dotenv

from migrar_json import importar
from persistencia import ErroPersistencia, PersistenciaPostgres

RAIZ = Path(__file__).resolve().parents[1]
SCHEMA_SQL = (RAIZ / 'sql' / '001_schema.sql').read_text(encoding='utf-8')


@unittest.skipUnless(os.environ.get('TEST_POSTGRES') == '1', 'Ative TEST_POSTGRES=1 em um banco de testes separado.')
class PostgresTest(unittest.TestCase):
    def setUp(self):
        load_dotenv(RAIZ / '.env', override=False)
        self.schema = 'teste_financeiro_' + uuid4().hex
        self.admin = psycopg.connect(autocommit=True)
        self.admin.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.addCleanup(self.limpar)
        self.ambiente = patch.dict(os.environ, {'PGOPTIONS': f'-c search_path={self.schema}'})
        self.ambiente.start()
        self.addCleanup(self.ambiente.stop)
        with psycopg.connect(autocommit=True) as conn:
            conn.execute(SCHEMA_SQL)
        self.repo = PersistenciaPostgres()

    def limpar(self):
        # Identificador gerado neste teste; nunca remove public ou tabelas do usuário.
        try:
            self.admin.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))
        finally:
            self.admin.close()

    def test_schema_reexecutavel_preserva_receita_existente(self):
        self.repo.registrar_receita('Existente', Decimal('25.10'))
        with psycopg.connect(autocommit=True) as conn:
            # Reconstitui a restrição original da tabela receitas da V0.4.
            conn.execute('ALTER TABLE receitas DROP CONSTRAINT receitas_valor_finito')
            conn.execute(SCHEMA_SQL)
        self.assertEqual(self.repo.calcular_totais(), (Decimal('25.10'), Decimal('0')))
        with self.assertRaises(ErroPersistencia):
            self.repo.registrar_receita('Inválido', Decimal('NaN'))

    def test_decimal_historico_e_parametros(self):
        descricao = "Cliente '); DROP TABLE receitas; --"
        self.repo.registrar_receita(descricao, Decimal('0.10'))
        self.repo.registrar_receita('Outro', Decimal('0.20'))
        self.repo.registrar_despesa('Custo', Decimal('0.05'))
        self.assertEqual(self.repo.calcular_totais(), (Decimal('0.30'), Decimal('0.05')))
        receitas, despesas = self.repo.carregar_historico()
        self.assertEqual(receitas[0]['descricao'], descricao)
        self.assertEqual(despesas[0]['valor'], Decimal('0.05'))
        self.repo.verificar_estrutura()

    def test_banco_recusa_zero_negativo_nan_e_overflow(self):
        for tabela in ['receitas', 'despesas']:
            registrar = getattr(self.repo, 'registrar_' + tabela[:-1])
            for valor in ['0', '-1', 'NaN', 'Infinity', '10000000000']:
                with self.subTest(tabela=tabela, valor=valor), self.assertRaises(ErroPersistencia):
                    registrar('Inválido', Decimal(valor))
        self.assertEqual(self.repo.calcular_totais(), (Decimal('0'), Decimal('0')))

    def test_importacao_atomica_e_nao_repetivel(self):
        dados = {'receitas': [('Legado', Decimal('100.10'))], 'despesas': [('Custo', Decimal('25.05'))]}
        importar(dados, 'a' * 64)
        self.assertEqual(self.repo.calcular_totais(), (Decimal('100.10'), Decimal('25.05')))
        with self.assertRaises(ValueError):
            importar(dados, 'b' * 64)
        self.assertEqual(self.repo.calcular_totais(), (Decimal('100.10'), Decimal('25.05')))

    def test_importacao_recusa_banco_com_dados(self):
        self.repo.registrar_receita('Existente', Decimal('1'))
        with self.assertRaises(ValueError):
            importar({'receitas': [('Legado', Decimal('2'))], 'despesas': []}, 'a' * 64)
        self.assertEqual(self.repo.calcular_totais()[0], Decimal('1'))

    def test_importacao_falha_desfaz_todos_os_registros(self):
        dados = {'receitas': [('Válida', Decimal('1'))], 'despesas': [('x' * 151, Decimal('2'))]}
        with self.assertRaises(ErroPersistencia):
            importar(dados, 'a' * 64)
        self.assertEqual(self.repo.calcular_totais(), (Decimal('0'), Decimal('0')))
        with psycopg.connect() as conn:
            self.assertEqual(conn.execute('SELECT count(*) FROM migracoes_json').fetchone()[0], 0)

    def test_cli_persistencia_apos_reinicio(self):
        def executar(entrada):
            resultado = subprocess.run([sys.executable, str(RAIZ / 'main.py')], input=entrada, text=True, capture_output=True, timeout=20)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            return resultado.stdout
        saida = executar('1\nServiço\n1000,10\n2\nCusto\n250,20\n3\n4\n5\n6\n')
        for esperado in ['Receita registrada com sucesso!', 'Despesa registrada com sucesso!', 'Saldo: R$ 749.90', 'Resultado: R$ 749.90', 'Serviço - R$ 1000.10', 'Custo - R$ 250.20']:
            self.assertIn(esperado, saida)
        self.assertIn('Saldo: R$ 749.90', executar('3\n6\n'))


if __name__ == '__main__':
    unittest.main()
