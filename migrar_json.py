"""Importação inicial opcional: valida sem gravar por padrão."""

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from persistencia import ErroPersistencia, conexao
from sistema_financeiro import validar_descricao, validar_valor


def ler_legado(caminho):
    conteudo = Path(caminho).read_bytes()
    dados = json.loads(conteudo.decode('utf-8-sig'), parse_float=Decimal)
    if not isinstance(dados, dict) or set(dados) != {'receitas', 'despesas'}:
        raise ValueError('O JSON deve conter apenas as listas receitas e despesas.')
    normalizado = {}
    for tipo in ('receitas', 'despesas'):
        if not isinstance(dados[tipo], list):
            raise ValueError(f'{tipo} deve ser uma lista.')
        normalizado[tipo] = []
        for item in dados[tipo]:
            if not isinstance(item, dict) or set(item) != {'descricao', 'valor'}:
                raise ValueError('Cada movimentação deve conter descricao e valor.')
            normalizado[tipo].append((
                validar_descricao(item['descricao']), validar_valor(item['valor'])
            ))
    if not any(normalizado.values()):
        raise ValueError('O JSON não contém movimentações para importar.')
    return normalizado, hashlib.sha256(conteudo).hexdigest()


def importar(dados, sha256):
    with conexao(escrita=True) as conn:
        # Impede duas importações concorrentes e novos lançamentos durante a cópia.
        conn.execute('LOCK TABLE migracoes_json, receitas, despesas IN EXCLUSIVE MODE')
        if conn.execute('SELECT 1 FROM migracoes_json WHERE id = 1').fetchone():
            raise ValueError('A importação inicial já foi realizada. Nada foi gravado.')
        if conn.execute('SELECT 1 FROM receitas UNION ALL SELECT 1 FROM despesas LIMIT 1').fetchone():
            raise ValueError('O banco deve estar vazio. Faça uma conciliação manual para evitar duplicidade.')
        with conn.cursor() as cursor:
            cursor.executemany(
                'INSERT INTO receitas (descricao, valor) VALUES (%s, %s)', dados['receitas']
            )
            cursor.executemany(
                'INSERT INTO despesas (descricao, valor) VALUES (%s, %s)', dados['despesas']
            )
        conn.execute('INSERT INTO migracoes_json (id, sha256) VALUES (1, %s)', (sha256,))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arquivo', type=Path)
    parser.add_argument('--confirmar', action='store_true', help='Gravar a importação única no banco vazio.')
    args = parser.parse_args()
    try:
        dados, sha256 = ler_legado(args.arquivo)
        print(f"JSON válido: {len(dados['receitas'])} receitas e {len(dados['despesas'])} despesas.")
        if not args.confirmar:
            print('Somente validação. Faça backup e use --confirmar para importar em banco vazio.')
            return 0
        importar(dados, sha256)
        print('Importação confirmada. O arquivo JSON original foi preservado.')
        return 0
    except (OSError, UnicodeError, ValueError, ErroPersistencia) as erro:
        # Erros de arquivo podem conter caminhos: não imprime seu conteúdo.
        if isinstance(erro, (OSError, UnicodeError, json.JSONDecodeError)):
            print('Não foi possível ler um JSON válido no arquivo informado. Nada foi importado.')
        else:
            print(erro)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
