from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from wallet import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidTransferError,
    InvalidWalletIdError,
    OperationType,
    Wallet,
)


def test_new_wallet_starts_empty() -> None:
    wallet = Wallet("alice")

    assert wallet.id == "alice"
    assert wallet.balance == Decimal("0.00")
    assert wallet.history == ()


@pytest.mark.parametrize("wallet_id", ["", " ", " alice", "alice ", 123, None])
def test_wallet_rejects_invalid_id(wallet_id: object) -> None:
    with pytest.raises(InvalidWalletIdError):
        Wallet(wallet_id)  # type: ignore[arg-type]


def test_deposit_updates_balance_and_history() -> None:
    wallet = Wallet("alice")

    operation = wallet.deposit(Decimal("10.0"))

    assert wallet.balance == Decimal("10.00")
    assert operation.type is OperationType.DEPOSIT
    assert operation.amount == Decimal("10.00")
    assert operation.balance_after == Decimal("10.00")
    assert operation.counterparty_wallet_id is None
    assert operation.transfer_id is None
    assert wallet.history == (operation,)


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0"),
        Decimal("-0"),
        Decimal("-1.00"),
        Decimal("0.001"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("1E+1000000"),
        "1.00",
        1,
        1.0,
        None,
    ],
)
def test_deposit_rejects_invalid_amount_without_changing_state(
    amount: object,
) -> None:
    wallet = Wallet("alice")

    with pytest.raises(InvalidAmountError):
        wallet.deposit(amount)  # type: ignore[arg-type]

    assert wallet.balance == Decimal("0.00")
    assert wallet.history == ()


def test_withdraw_updates_balance_and_history() -> None:
    wallet = Wallet("alice")
    wallet.deposit(Decimal("25.00"))

    operation = wallet.withdraw(Decimal("7.50"))

    assert wallet.balance == Decimal("17.50")
    assert operation.type is OperationType.WITHDRAWAL
    assert operation.amount == Decimal("7.50")
    assert operation.balance_after == Decimal("17.50")
    assert wallet.history[-1] == operation


def test_withdraw_rejects_insufficient_funds_without_changing_state() -> None:
    wallet = Wallet("alice")
    wallet.deposit(Decimal("5.00"))
    history_before = wallet.history

    with pytest.raises(InsufficientFundsError):
        wallet.withdraw(Decimal("5.01"))

    assert wallet.balance == Decimal("5.00")
    assert wallet.history == history_before


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("0.001"), 1.0])
def test_withdraw_rejects_invalid_amount_without_changing_state(
    amount: object,
) -> None:
    wallet = Wallet("alice")
    wallet.deposit(Decimal("5.00"))
    history_before = wallet.history

    with pytest.raises(InvalidAmountError):
        wallet.withdraw(amount)  # type: ignore[arg-type]

    assert wallet.balance == Decimal("5.00")
    assert wallet.history == history_before


def test_transfer_creates_linked_history_entries() -> None:
    source = Wallet("alice")
    destination = Wallet("bob")
    source.deposit(Decimal("20.00"))

    outgoing, incoming = source.transfer_to(destination, Decimal("7.25"))

    assert source.balance == Decimal("12.75")
    assert destination.balance == Decimal("7.25")
    assert outgoing.type is OperationType.TRANSFER_OUT
    assert outgoing.counterparty_wallet_id == "bob"
    assert outgoing.balance_after == Decimal("12.75")
    assert incoming.type is OperationType.TRANSFER_IN
    assert incoming.counterparty_wallet_id == "alice"
    assert incoming.balance_after == Decimal("7.25")
    assert outgoing.transfer_id is not None
    assert outgoing.transfer_id == incoming.transfer_id


def test_transfer_rejects_same_wallet_without_changing_state() -> None:
    wallet = Wallet("alice")
    wallet.deposit(Decimal("10.00"))
    history_before = wallet.history

    with pytest.raises(InvalidTransferError):
        wallet.transfer_to(wallet, Decimal("1.00"))

    assert wallet.balance == Decimal("10.00")
    assert wallet.history == history_before


def test_transfer_rejects_non_wallet_destination() -> None:
    wallet = Wallet("alice")

    with pytest.raises(InvalidTransferError):
        wallet.transfer_to(object(), Decimal("1.00"))  # type: ignore[arg-type]


def test_history_snapshot_and_entries_are_immutable() -> None:
    wallet = Wallet("alice")
    operation = wallet.deposit(Decimal("1.00"))
    history = wallet.history

    with pytest.raises(AttributeError):
        history.append(operation)  # type: ignore[attr-defined]
    with pytest.raises(FrozenInstanceError):
        operation.amount = Decimal("999.00")  # type: ignore[misc]

    wallet.deposit(Decimal("2.00"))
    assert len(history) == 1
    assert len(wallet.history) == 2
