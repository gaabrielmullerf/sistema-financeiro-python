"""Acesso ao PostgreSQL; cada operação usa e fecha sua própria conexão."""

from contextlib import contextmanager
from pathlib import Path

import psycopg
from dotenv import load_dotenv


class ErroPersistencia(Exception):
    """Erro seguro para exibição, sem expor credenciais ou detalhes SQL."""


@contextmanager
def conexao(escrita=False):
    load_dotenv(Path(__file__).with_name('.env'), override=False)
    try:
        # libpq lê PGHOST, PGPORT, PGDATABASE, PGUSER e PGPASSWORD.
        # O contexto confirma a transação no sucesso e desfaz em caso de erro.
        with psycopg.connect(connect_timeout=5) as conn:
            conn.execute("SET LOCAL statement_timeout = '10s'")
            yield conn
    except psycopg.Error as erro:
        if escrita:
            mensagem = (
                'Gravação não confirmada pelo banco. Confira o histórico antes de '
                'tentar novamente, para evitar duplicidade.'
            )
        else:
            mensagem = (
                'Não foi possível consultar o PostgreSQL. Confira o serviço, '
                'a configuração da conexão e a execução de sql/001_schema.sql.'
            )
        raise ErroPersistencia(mensagem) from erro


class PersistenciaPostgres:
    def verificar_estrutura(self):
        with conexao() as conn:
            conn.execute('SELECT id, descricao, valor FROM receitas LIMIT 0')
            conn.execute('SELECT id, descricao, valor FROM despesas LIMIT 0')

    def registrar_receita(self, descricao, valor):
        with conexao(escrita=True) as conn:
            conn.execute(
                'INSERT INTO receitas (descricao, valor) VALUES (%s, %s)',
                (descricao, valor),
            )

    def registrar_despesa(self, descricao, valor):
        with conexao(escrita=True) as conn:
            conn.execute(
                'INSERT INTO despesas (descricao, valor) VALUES (%s, %s)',
                (descricao, valor),
            )

    def calcular_totais(self):
        with conexao() as conn:
            return conn.execute('''
                SELECT
                    (SELECT COALESCE(SUM(valor), 0) FROM receitas),
                    (SELECT COALESCE(SUM(valor), 0) FROM despesas)
            ''').fetchone()

    def carregar_historico(self):
        with conexao() as conn:
            linhas = conn.execute('''
                SELECT 'receita' AS tipo, id, descricao, valor FROM receitas
                UNION ALL
                SELECT 'despesa' AS tipo, id, descricao, valor FROM despesas
                ORDER BY tipo, id
            ''').fetchall()
        receitas, despesas = [], []
        for tipo, identificador, descricao, valor in linhas:
            destino = receitas if tipo == 'receita' else despesas
            destino.append({'id': identificador, 'descricao': descricao, 'valor': valor})
        return receitas, despesas
