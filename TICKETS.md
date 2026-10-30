# Tickets do projeto Wallet

Os tickets abaixo são pequenos de propósito. Cada entrega deve atender a todos
os critérios de aceitação e incluir ou atualizar os testes correspondentes.

## WAL-001 — Criar carteira e consultar saldo

**Objetivo:** criar carteiras em memória e consultar seus saldos.

**Critérios de aceitação:**

- uma carteira é criada com ID explícito, saldo `Decimal("0.00")` e histórico
  vazio;
- IDs vazios, com espaços nas extremidades ou que não sejam `str` são
  rejeitados;
- um ID duplicado gera `WalletAlreadyExistsError` e não substitui a carteira;
- consultar um ID inexistente gera `WalletNotFoundError`.

**Validação:** `python -m pytest tests/unit/test_service.py`.

## WAL-002 — Depositar dinheiro

**Objetivo:** adicionar dinheiro a uma carteira existente.

**Critérios de aceitação:**

- o depósito atualiza o saldo exatamente, usando `Decimal`;
- o histórico recebe uma operação `DEPOSIT` com valor e saldo resultante;
- somente valores finitos, positivos e representáveis em centavos são aceitos;
- falhas não alteram saldo nem histórico.

**Validação:** `python -m pytest tests/unit/test_wallet.py -k deposit`.

## WAL-003 — Sacar dinheiro

**Objetivo:** retirar dinheiro sem permitir saldo negativo.

**Critérios de aceitação:**

- um saque válido atualiza saldo e adiciona uma operação `WITHDRAWAL`;
- sacar exatamente o saldo total é permitido;
- valor maior que o saldo gera `InsufficientFundsError`;
- valor inválido ou saldo insuficiente não cria histórico.

**Validação:** `python -m pytest tests/unit/test_wallet.py -k withdraw`.

## WAL-004 — Transferir entre carteiras

**Objetivo:** mover dinheiro atomicamente entre duas carteiras.

**Critérios de aceitação:**

- origem e destino devem existir e ser diferentes;
- uma transferência válida debita a origem e credita o destino pelo mesmo
  valor;
- os dois históricos recebem registros vinculados pelo mesmo `transfer_id`;
- saldo insuficiente, valor inválido ou transferência inconsistente não altera
  nenhuma das carteiras;
- a soma dos saldos não muda por causa de uma transferência.

**Validação:** `python -m pytest tests/integration -k transfer`.

## WAL-005 — Consultar histórico

**Objetivo:** expor as operações sem permitir alteração externa.

**Critérios de aceitação:**

- as operações aparecem na ordem em que ocorreram;
- cada registro contém tipo, valor e saldo resultante;
- transferências também contêm contraparte e identificador compartilhado;
- o resultado é uma tupla e seus registros são imutáveis;
- históricos de carteiras diferentes são independentes.

**Validação:** `python -m pytest -k history`.

## WAL-006 — Cobrir regras com testes unitários

**Objetivo:** testar as regras de negócio isoladamente.

**Critérios de aceitação:**

- há casos felizes, erros e limites para IDs, valores, depósitos e saques;
- os testes usam somente o contrato público para observar resultados;
- cada teste deixa clara uma regra do requisito;
- a suíte unitária passa com `python -m pytest tests/unit`.

## WAL-007 — Adicionar testes de integração e regressão

**Objetivo:** validar jornadas completas e impedir o retorno de bugs conhecidos.

**Critérios de aceitação:**

- há uma jornada com criação, depósito, transferência, saque e histórico;
- falhas de transferência comprovam atomicidade;
- há regressões para saque do saldo total e precisão decimal;
- a suíte completa atinge 100% de cobertura de linhas sem ignorar código.

**Validação:**
`python -m pytest --cov=wallet --cov-report=term-missing --cov-fail-under=100`.

## WAL-008 — Configurar integração contínua

**Objetivo:** executar a validação automaticamente no GitHub.

**Critérios de aceitação:**

- `.github/workflows/tests.yml` reage a push em `main` e PR para `main`;
- o job se chama `testes` e usa Python 3.12;
- as dependências vêm de `requirements-dev.txt`;
- falhas de teste ou cobertura fazem o workflow falhar.

## WAL-009 — Documentar contribuição e validação por IA

**Objetivo:** permitir que outra pessoa reproduza e avalie o projeto.

**Critérios de aceitação:**

- o README ensina instalação, uso e execução dos testes;
- o tutorial explica testes, CI, PRs, proteção da branch e revisão de agentes;
- existe um exercício completo de bug proposital e correção;
- nenhum bug proposital permanece em `main`.
