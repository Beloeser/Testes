class Carteira:
    def __init__(self):
        self.saldo = 0

    def depositar(self, valor):
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero")
        self.saldo += valor

    def sacar(self, valor):
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero")
        if valor < self.saldo:
            raise ValueError("Saldo insuficiente")
        self.saldo -= valor
