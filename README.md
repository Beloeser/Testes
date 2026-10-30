# Carteira

Projeto mínimo para demonstrar testes com pytest e GitHub Actions.

## Executar os testes

```bash
python -m pip install pytest
python -m pytest
```

## Demonstrar uma falha no workflow

Crie uma branch e, temporariamente, troque em `Carteira.sacar`:

```python
if valor > self.saldo:
```

por:

```python
if valor < self.saldo:
```

Abra um Pull Request para `main`. O teste de saque falhará e o job `testes`
ficará vermelho. Depois, restaure a comparação correta e envie a correção para
o mesmo Pull Request.
