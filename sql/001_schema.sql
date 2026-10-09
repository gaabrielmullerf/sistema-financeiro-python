-- Execute no banco sistema_financeiro. Não apaga tabelas ou registros.
BEGIN;

CREATE TABLE IF NOT EXISTS receitas (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    valor NUMERIC(12,2) NOT NULL CHECK (valor > 0)
);

CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    valor NUMERIC(12,2) NOT NULL CHECK (valor > 0)
);

-- PostgreSQL considera NaN maior que números: CHECK (valor > 0) não basta.
-- Acrescenta proteção também à tabela receitas já existente na V0.4.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                   WHERE conrelid = 'receitas'::regclass AND conname = 'receitas_valor_finito') THEN
        ALTER TABLE receitas ADD CONSTRAINT receitas_valor_finito
            CHECK (valor > 0 AND valor <> 'NaN'::numeric);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                   WHERE conrelid = 'despesas'::regclass AND conname = 'despesas_valor_finito') THEN
        ALTER TABLE despesas ADD CONSTRAINT despesas_valor_finito
            CHECK (valor > 0 AND valor <> 'NaN'::numeric);
    END IF;
END $$;

-- Marca uma única importação inicial; registros e marcador são atômicos.
CREATE TABLE IF NOT EXISTS migracoes_json (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    sha256 CHAR(64) NOT NULL,
    executada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
