import pytest

from carteira import Carteira


def test_deposito_valido():
    carteira = Carteira()
    carteira.depositar(100)

    assert carteira.saldo == 100


def test_saque_valido():
    carteira = Carteira()
    carteira.depositar(100)
    carteira.sacar(40)

    assert carteira.saldo == 60


def test_saque_com_saldo_insuficiente():
    carteira = Carteira()

    with pytest.raises(ValueError):
        carteira.sacar(1)


def test_deposito_negativo():
    carteira = Carteira()

    with pytest.raises(ValueError):
        carteira.depositar(-10)
