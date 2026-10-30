# Tutorial: testes, CI e validação de agentes de IA

Este guia usa o Wallet para mostrar um ciclo de entrega verificável. A ideia
central é simples: uma resposta convincente de um agente de IA não substitui
evidência executável.

## 1. Requisitos viram testes

Os testes deste projeto partem das regras de negócio, não das linhas internas
da implementação:

- **unitários** verificam uma regra isolada, como rejeitar valor negativo;
- **integração** verifica uma jornada entre componentes, como transferir entre
  duas carteiras e consultar os dois históricos;
- **regressão** registra um comportamento que já falhou ou representa um risco
  conhecido, como permitir o saque do saldo exato.

Um bom teste segue o arranjo **preparar, agir, verificar**. Ele observa saldo,
histórico e exceções pela API pública. Assim, a implementação pode ser
refatorada sem reescrever requisitos.

## 2. Ciclo vermelho, verde e refatoração

1. **Vermelho:** escreva um teste para o critério de aceitação e confirme que
   ele falha pelo motivo esperado.
2. **Verde:** implemente a menor mudança que faz o teste passar.
3. **Refatoração:** melhore nomes e estrutura mantendo a suíte verde.

Execute rapidamente um grupo:

```bash
python -m pytest tests/unit -q
```

Antes de entregar, execute a mesma validação da CI:

```bash
python -m pytest --cov=wallet --cov-report=term-missing --cov-fail-under=100
```

Cobertura mostra quais linhas foram exercitadas; ela não prova, sozinha, que os
testes verificam as regras certas. Leia as asserções e confira os casos
negativos e de borda.

## 3. Pull Request e GitHub Actions

Trabalhe em uma branch por ticket:

```bash
git switch main
git pull --ff-only
git switch -c feat/wal-004-transferencias
# implemente e execute os testes
git add wallet tests
git diff --cached
git commit -m "feat: implementa transferencias atomicas"
git push -u origin feat/wal-004-transferencias
```

No GitHub, abra um Pull Request com base `main`. Descreva o requisito, decisões
de escopo, testes executados e riscos. O workflow roda porque o PR aponta para
`main`; o mesmo workflow também roda depois de cada push em `main`.

O job `testes` instala Python 3.12 e as dependências, roda o pytest e exige a
cobertura configurada. O shell devolve o código de saída do pytest: se um teste
falhar, se a coleta quebrar ou se a cobertura ficar abaixo do limite, o job
falha.

### Tornar o check obrigatório

Depois que o workflow executar ao menos uma vez:

1. abra **Settings > Branches** no repositório GitHub;
2. crie uma branch protection rule para `main`;
3. habilite **Require a pull request before merging**;
4. habilite **Require status checks to pass before merging**;
5. selecione o status check `testes` e salve.

Sem essa regra, o Actions informa a falha, mas o GitHub não necessariamente
impede um usuário com permissão de fazer merge.

## 4. Como validar uma entrega de um agente de IA

Nunca valide apenas pelo resumo escrito pelo agente. Use esta lista:

- compare a solicitação com o diff e procure mudanças fora do escopo;
- confirme que regras monetárias usam `Decimal`, nunca `float`;
- procure caminhos que alterem estado antes de concluir todas as validações;
- leia os testes e associe cada um a um critério de aceitação;
- confira casos de erro, borda e invariância após falhas;
- desconfie de testes acoplados a atributos internos ou que não tenham
  asserções relevantes;
- execute a suíte completa em um ambiente limpo;
- confira o relatório de cobertura e inspecione linhas não exercitadas;
- confirme que a CI usa a versão de Python e o comando documentados;
- revise dependências e arquivos gerados antes do commit.

Se um agente alterar implementação e testes ao mesmo tempo, tente formular um
teste adicional a partir do requisito original. Isso reduz o risco de ambos
compartilharem a mesma interpretação errada.

## 5. Exercício: um bug deve bloquear o merge

O código final deste repositório está correto. O exercício abaixo cria o bug
somente em uma branch temporária e depois o corrige no mesmo Pull Request.

### Passo A — Confirme a base verde

```bash
git switch main
git pull --ff-only
python -m pytest
git switch -c demo/bug-saque-total
```

### Passo B — Introduza o bug proposital

Em `wallet/wallet.py`, dentro de `_ensure_sufficient_funds`, troque
temporariamente:

```python
if amount > self._balance:
```

por:

```python
if amount >= self._balance:
```

Esse bug trata o saque de todo o saldo como se fosse insuficiente. Não altere o
teste de regressão para acomodar o defeito.

### Passo C — Observe a evidência local

```bash
python -m pytest tests/regression/test_regressions.py \
  -k withdrawing_exact_balance
```

O teste deve falhar com `InsufficientFundsError`. Esse resultado confirma que
o teste detecta o defeito planejado.

### Passo D — Abra o Pull Request com falha

```bash
git add wallet/wallet.py
git commit -m "demo: introduz bug no saque total"
git push -u origin demo/bug-saque-total
```

Abra um PR para `main`. O GitHub Actions executará o job `testes`, que ficará
vermelho. Com a proteção descrita acima, o merge ficará bloqueado.

### Passo E — Corrija no mesmo Pull Request

Restaure a comparação correta (`>`), execute toda a suíte e envie a correção:

```bash
python -m pytest --cov=wallet --cov-report=term-missing --cov-fail-under=100
git add wallet/wallet.py
git commit -m "fix: permite sacar o saldo total"
git push
```

O push atualiza o mesmo PR. O check `testes` deve ficar verde e liberar o merge.
Não faça merge do commit que contém o bug isoladamente e exclua a branch de
demonstração depois do exercício.
