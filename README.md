# Sistema Financeiro — V0.5

Aplicação Python de terminal para pequenos negócios. Receitas, despesas, saldo,
resumo e histórico agora usam PostgreSQL. O menu continua com as mesmas seis
opções. Não há API, interface web ou autenticação nesta versão.

## Decisões da V0.5

- **Psycopg 3** é o driver que permite ao Python conversar com PostgreSQL.
- **Decimal + NUMERIC(12,2)** preservam centavos sem a imprecisão de `float`.
- Aceitamos ponto ou vírgula decimal: `125.50` e `125,50`. Não use separador de
  milhares. Valores com frações de centavo são recusados, sem arredondamento
  silencioso; zero, negativos, NaN, infinito e valores acima de `9999999999,99`
  também são recusados. Descrições precisam ter 1 a 150 caracteres após remover
  espaços das extremidades.
- O banco é a fonte dos dados. Não há cópia em listas mantida entre operações.
- Cada operação abre uma conexão e uma transação, faz commit somente no sucesso,
  rollback em caso de erro e fecha a conexão. Consultas têm limite de 10 segundos
  e a conexão tem limite de 5 segundos.
- SQL parametrizado mantém os valores do usuário separados dos comandos SQL.
- `python-dotenv` lê configurações locais do `.env`; variáveis já definidas no
  processo têm prioridade. Não registre senhas no código ou no Git.
- Uma falha de gravação nunca gera mensagem de sucesso. Se a conexão cair durante
  o commit, o resultado pode ser incerto: consulte o histórico antes de repetir
  um cadastro. Não há repetição automática de gravações.

## Referência da V0.4

O commit original é `cd01f3acd8c9a35db3b817ff116875b40fb388ca`, preservado localmente
pela tag `referencia-v0.4`. A tag não foi enviada ao GitHub. Você pode consultar a
versão antiga sem alterar seus arquivos:

```powershell
git show cd01f3a:main.py
git show cd01f3a:persistencia.py
```

O `dados.json` antigo não é apagado nem importado automaticamente. Faça backup
antes de qualquer migração. A V0.5 passa a exibir somente registros do PostgreSQL;
registros do JSON aparecem após a importação opcional.

## Como executar no Windows (PowerShell do VS Code)

### 1. Abra a pasta do projeto

No VS Code, use **Arquivo > Abrir Pasta** e selecione `sistema-financeiro-python`.
Depois abra **Terminal > Novo Terminal**. Os comandos abaixo devem ser executados
na pasta que contém `main.py` e `requirements.txt`.

Use Python 3.10 ou superior; esta implementação foi testada com Python 3.12.

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Instalamos `psycopg[binary]` (driver pronto para uso, sem compilação) e
`python-dotenv` (leitura do `.env`). Não é necessário ativar o ambiente virtual:
chamar seu `python.exe` diretamente evita problemas com a política do PowerShell.

### 2. Configure a conexão

```powershell
Copy-Item .env.example .env
```

Se você já possui `.env`, edite-o; não sobrescreva suas configurações.
Abra `.env` no VS Code e configure:

- `PGHOST`: `localhost` para seu PostgreSQL local.
- `PGPORT`: normalmente `5432`.
- `PGDATABASE`: `sistema_financeiro`.
- `PGUSER`: seu usuário PostgreSQL, normalmente `postgres` no ambiente local.
- `PGPASSWORD`: a senha desse usuário, inserida somente no seu computador.

Se a senha contiver `#`, espaços ou outros caracteres especiais, use as regras de
aspas do formato dotenv. Não envie o `.env`, prints com a senha ou credenciais.
O arquivo está no `.gitignore`. O `.env.example` não contém senha.

O pgAdmin é uma interface de administração: ele não precisa ficar aberto para o
programa funcionar. O serviço PostgreSQL precisa estar rodando. Este código na
nuvem não acessa o PostgreSQL do seu computador.

### 3. Prepare o banco usando pgAdmin 4

1. Conecte-se ao servidor PostgreSQL 18 que você já instalou.
2. Selecione **Databases > sistema_financeiro**. Não execute no banco `postgres`.
3. Se já houver dados importantes, faça **Backup** do banco antes de continuar.
4. Abra **Query Tool**, carregue `sql/001_schema.sql` e execute o arquivo inteiro.
5. Atualize **Schemas > public > Tables**; devem aparecer `receitas`, `despesas`
   e `migracoes_json`.

Seu banco `sistema_financeiro` e a tabela `receitas` já existentes são reutilizados.
O script usa `CREATE TABLE IF NOT EXISTS` e não remove registros. Pode ser
executado novamente. Ele adiciona restrições para recusar NaN, que o PostgreSQL
considera maior que números normais. Se já houver valores inválidos, a transação
falha sem apagar dados: execute `ROLLBACK;` no Query Tool e investigue os registros
antes de corrigir. Não remova tabelas para contornar erros.

O script pressupõe a estrutura de `receitas` informada na V0.4 (id identity,
descricao VARCHAR(150), valor NUMERIC(12,2)). Não converte automaticamente tabelas
com estruturas diferentes. No uso comum, as tabelas ficam no schema `public`.

### 4. Inicie e confira

```powershell
.\.venv\Scripts\python.exe main.py
```

- Opção **1**: registre receita `Serviço` com valor `1000,10`.
- Opção **2**: registre despesa `Custo` com valor `250,20`.
- Opções **3**, **4** e **5**: confira saldo, resumo e histórico.
- Em um banco vazio, o saldo será `749.90`; se já houver registros, some esses
  novos lançamentos aos totais existentes.
- Use **6**, abra novamente e consulte o saldo. Os dados devem permanecer.
- Experimente `0`, `-10`, `abc` e `1,001`: nenhum deles deve ser cadastrado.

Esses cadastros são registros reais. Prefira um banco separado de testes se você
já utiliza o banco com dados importantes.

Para inspecionar pelo Query Tool:

```sql
SELECT id, descricao, valor FROM receitas ORDER BY id;
SELECT id, descricao, valor FROM despesas ORDER BY id;
```

### 5. Problemas comuns

- **Não foi possível consultar o PostgreSQL**: confira o serviço, host, porta,
  nome do banco, usuário, senha e se o script SQL foi executado no banco certo.
- **Gravação não confirmada**: confira a conexão, as permissões e o histórico
  antes de cadastrar novamente. Uma queda durante o commit pode ter ocorrido
  depois de o servidor salvar a movimentação.
- **ModuleNotFoundError**: execute com `.venv\Scripts\python.exe` e reinstale
  `requirements.txt` usando esse mesmo Python.
- **Porta diferente de 5432**: ajuste `PGPORT` no `.env`.

Não compartilhe senha ou o `.env` para diagnosticar problemas. As mensagens da
aplicação evitam expor detalhes internos ou credenciais.

## Importação opcional do JSON da V0.4

A aplicação normal nunca abre nem modifica `dados.json`. Há um utilitário separado
para importar os dados uma única vez, somente se ambas as tabelas financeiras
estiverem vazias. Se seu banco já contém lançamentos, ele recusa a importação para
não duplicar registros; será necessária uma conciliação manual antes de definir
outra estratégia.

1. Faça backup do JSON e do banco. Guarde uma cópia fora do repositório.
2. Valide o JSON, sem conectar ao banco ou gravar:

```powershell
.\.venv\Scripts\python.exe migrar_json.py .\dados.json
```

3. Confira as quantidades e a configuração do banco. Só quando decidir importar:

```powershell
.\.venv\Scripts\python.exe migrar_json.py .\dados.json --confirmar
```

4. Consulte saldo e histórico e compare com o JSON original.

A importação valida todos os itens antes de gravar. Cadastros e marcador de
importação usam uma única transação. Se houver falha, nenhum item parcial fica
salvo. Um bloqueio impede importações concorrentes. `migracoes_json` registra o
hash do arquivo e impede outra importação inicial, mesmo que o arquivo tenha
sido editado ou renomeado. Não apague esse marcador para repetir a importação.
O JSON permanece intacto. Valores legados com frações de centavo são recusados:
defina a correção explicitamente em uma cópia, preservando o original.

## Testes

### Sem banco (regras e comportamento do terminal)

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_financeiro.py -v
```

### Com PostgreSQL (integração)

No pgAdmin, crie um banco **separado**, por exemplo `sistema_financeiro_testes`.
Não é necessário executar o SQL nesse banco antes dos testes. O usuário precisa
ter permissão de criar schemas.

No terminal, reutilize host, porta e usuário do `.env`, mas aponte explicitamente
para o banco de testes. As variáveis do processo têm prioridade sobre o `.env`:

```powershell
$env:PGDATABASE = "sistema_financeiro_testes"
$env:TEST_POSTGRES = "1"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Remove-Item Env:TEST_POSTGRES
Remove-Item Env:PGDATABASE
```

Os testes criam schemas `teste_financeiro_<identificador aleatório>` e removem
somente esses schemas ao terminar. Nunca removem `public` nem seus dados. Se um
processo for interrompido abruptamente, pode restar um schema de teste. Não use um
banco de produção. Sem `TEST_POSTGRES=1`, a suíte de integração é marcada como
**skipped**, não como integração validada.

## Arquivos

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Menu, inicialização e tratamento de falhas de persistência. |
| `sistema_financeiro.py` | Validações com Decimal e apresentação das operações. |
| `persistencia.py` | Conexões, transações e SQL parametrizado. |
| `sql/001_schema.sql` | Criação segura e repetível de tabelas e restrições. |
| `migrar_json.py` | Validação e importação inicial opcional, sem apagar JSON. |
| `.env.example` | Modelo de conexão sem credenciais. |
| `.gitignore` | Proteção de `.env`, dados locais e arquivos gerados. |
| `requirements.txt` | Dependências da V0.5. |
| `tests/test_financeiro.py` | Testes sem banco de validações e apresentação. |
| `tests/test_postgres.py` | Integração real em schemas temporários. |

## Próxima etapa

A revisão e a validação no PostgreSQL 18 do Windows encerram a V0.5. Para a V0.6,
ampliar cenários de testes, organizar verificações de qualidade e automatizá-las
no CI. API, autenticação e interface web continuam para etapas posteriores.

## Validação realizada na nuvem

Foram executados 19 testes com Python 3.12 e PostgreSQL 17.11: 12 sem banco e 7 de
integração real, incluindo o menu em processos separados, persistência após
reinício, precisão decimal, entradas SQL tratadas como texto, restrições,
preservação de dados ao reaplicar o schema e rollback da importação.
Todos passaram. Sintaxe, consistência das dependências e whitespace do diff
também foram verificados. O PostgreSQL 18 no Windows ainda deve ser validado
no seu computador; o resultado da nuvem não substitui essa verificação.
