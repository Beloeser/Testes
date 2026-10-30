from decimal import Decimal

import pytest

from wallet import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidTransferError,
    OperationType,
    WalletNotFoundError,
    WalletService,
)


def test_complete_two_wallet_journey() -> None:
    service = WalletService()
    service.create_wallet("alice")
    service.create_wallet("bob")

    service.deposit("alice", Decimal("100.00"))
    service.deposit("bob", Decimal("10.00"))
    outgoing, incoming = service.transfer("alice", "bob", Decimal("35.50"))
    withdrawal = service.withdraw("bob", Decimal("5.25"))

    assert service.get_balance("alice") == Decimal("64.50")
    assert service.get_balance("bob") == Decimal("40.25")
    assert [entry.type for entry in service.get_history("alice")] == [
        OperationType.DEPOSIT,
        OperationType.TRANSFER_OUT,
    ]
    assert [entry.type for entry in service.get_history("bob")] == [
        OperationType.DEPOSIT,
        OperationType.TRANSFER_IN,
        OperationType.WITHDRAWAL,
    ]
    assert outgoing.transfer_id == incoming.transfer_id
    assert withdrawal.balance_after == Decimal("40.25")


def test_transfers_in_both_directions_preserve_total_money() -> None:
    service = WalletService()
    service.create_wallet("alice")
    service.create_wallet("bob")
    service.deposit("alice", Decimal("50.00"))
    service.deposit("bob", Decimal("25.00"))

    service.transfer("alice", "bob", Decimal("12.00"))
    service.transfer("bob", "alice", Decimal("7.00"))

    alice_balance = service.get_balance("alice")
    bob_balance = service.get_balance("bob")
    assert alice_balance == Decimal("45.00")
    assert bob_balance == Decimal("30.00")
    assert alice_balance + bob_balance == Decimal("75.00")


def test_failed_transfer_does_not_prevent_later_valid_transfer() -> None:
    service = WalletService()
    service.create_wallet("alice")
    service.create_wallet("bob")
    service.deposit("alice", Decimal("10.00"))

    with pytest.raises(InsufficientFundsError):
        service.transfer("alice", "bob", Decimal("10.01"))

    service.transfer("alice", "bob", Decimal("10.00"))

    assert service.get_balance("alice") == Decimal("0.00")
    assert service.get_balance("bob") == Decimal("10.00")


def test_transfer_validates_existing_destination_and_distinct_wallets() -> None:
    service = WalletService()
    service.create_wallet("alice")
    service.deposit("alice", Decimal("10.00"))
    history_before = service.get_history("alice")

    with pytest.raises(WalletNotFoundError):
        service.transfer("alice", "missing", Decimal("1.00"))
    with pytest.raises(InvalidTransferError):
        service.transfer("alice", "alice", Decimal("1.00"))

    assert service.get_balance("alice") == Decimal("10.00")
    assert service.get_history("alice") == history_before


def test_transfer_rejects_unknown_source_without_changing_destination() -> None:
    service = WalletService()
    service.create_wallet("bob")
    service.deposit("bob", Decimal("3.00"))
    history_before = service.get_history("bob")

    with pytest.raises(WalletNotFoundError):
        service.transfer("missing", "bob", Decimal("1.00"))

    assert service.get_balance("bob") == Decimal("3.00")
    assert service.get_history("bob") == history_before


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("0.001"), 1.0])
def test_transfer_rejects_invalid_amount_without_changing_either_wallet(
    amount: object,
) -> None:
    service = WalletService()
    service.create_wallet("alice")
    service.create_wallet("bob")
    service.deposit("alice", Decimal("10.00"))
    alice_history_before = service.get_history("alice")
    bob_history_before = service.get_history("bob")

    with pytest.raises(InvalidAmountError):
        service.transfer("alice", "bob", amount)  # type: ignore[arg-type]

    assert service.get_balance("alice") == Decimal("10.00")
    assert service.get_balance("bob") == Decimal("0.00")
    assert service.get_history("alice") == alice_history_before
    assert service.get_history("bob") == bob_history_before
