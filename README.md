# Wallet

Wallet é um projeto educacional, inspirado em um case técnico do Nubank, para
praticar desenvolvimento e validação de software com agentes de IA, testes
automatizados e integração contínua.

O sistema é intencionalmente pequeno: uma carteira digital em memória, sem
frontend, API ou banco de dados.

## Funcionalidades

- criar uma carteira com identificador único;
- consultar saldo;
- depositar e sacar dinheiro;
- transferir entre duas carteiras;
- consultar o histórico cronológico de operações.

## Regras de negócio

- Todo valor monetário é um `Decimal`, finito, maior que zero e representável
  em centavos. `float`, `int` e `str` são rejeitados.
- Carteiras começam com saldo `Decimal("0.00")`.
- IDs são strings não vazias, sem espaços no começo ou no fim, e não podem se
  repetir.
- Saques e transferências não podem exceder o saldo disponível.
- A origem e o destino de uma transferência devem existir e ser diferentes.
- Uma operação inválida não altera saldo nem histórico.
- O histórico é retornado como uma tupla de registros imutáveis.

Erros esperados são representados por exceções de domínio em
`wallet.exceptions`, como `InvalidAmountError`, `WalletNotFoundError` e
`InsufficientFundsError`.

## Requisitos e instalação

- Python 3.12 ou superior;
- `pip`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

No Windows PowerShell, ative o ambiente com
`.venv\Scripts\Activate.ps1`.

## Uso

```python
from decimal import Decimal

from wallet import WalletService

service = WalletService()
service.create_wallet("alice")
service.create_wallet("bob")
service.deposit("alice", Decimal("100.00"))
service.transfer("alice", "bob", Decimal("25.00"))

assert service.get_balance("alice") == Decimal("75.00")
assert service.get_balance("bob") == Decimal("25.00")
print(service.get_history("alice"))
```

## Testes e cobertura

Execute toda a suíte:

```bash
python -m pytest
```

Execute da mesma forma que a integração contínua:

```bash
python -m pytest --cov=wallet --cov-report=term-missing --cov-fail-under=100
```

Os testes ficam separados por intenção:

- `tests/unit`: regras isoladas das entidades e do serviço;
- `tests/integration`: jornadas completas entre várias carteiras;
- `tests/regression`: bugs que não podem reaparecer.

O workflow `.github/workflows/tests.yml` executa o job obrigatório `testes` em
todo push para `main` e em todo Pull Request direcionado a `main`. Qualquer
teste ou limite de cobertura que falhar encerra o job com erro.

## Estrutura

```text
wallet/                  implementação do domínio e serviço
tests/unit/              testes unitários
tests/integration/       testes de integração
tests/regression/        testes de regressão
.github/workflows/       integração contínua
TICKETS.md               backlog com critérios de aceitação
TUTORIAL.md              guia didático de testes, PRs, CI e agentes
```

## Fluxo de contribuição

1. Escolha um ticket em [TICKETS.md](TICKETS.md).
2. Crie uma branch curta a partir de `main`.
3. Implemente apenas o escopo do ticket e execute os testes localmente.
4. Revise o diff e abra um Pull Request para `main`.
5. Faça merge somente após revisão e aprovação do check `testes`.

Veja [TUTORIAL.md](TUTORIAL.md) para configurar a proteção da branch, validar
entregas de agentes de IA e executar a demonstração de um bug bloqueado pela
CI.
# Testes
