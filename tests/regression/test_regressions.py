from decimal import Decimal

import pytest

from wallet import InsufficientFundsError, InvalidAmountError, WalletService


def test_withdrawing_exact_balance_is_allowed() -> None:
    """Regression: comparing with >= would reject a valid full withdrawal."""
    service = WalletService()
    service.create_wallet("alice")
    service.deposit("alice", Decimal("10.00"))

    service.withdraw("alice", Decimal("10.00"))

    assert service.get_balance("alice") == Decimal("0.00")


def test_decimal_arithmetic_does_not_introduce_binary_rounding_error() -> None:
    service = WalletService()
    service.create_wallet("alice")

    service.deposit("alice", Decimal("0.10"))
    service.deposit("alice", Decimal("0.20"))

    assert service.get_balance("alice") == Decimal("0.30")


def test_failed_transfer_is_atomic_for_both_wallets_and_histories() -> None:
    service = WalletService()
    service.create_wallet("alice")
    service.create_wallet("bob")
    service.deposit("alice", Decimal("4.00"))
    alice_history_before = service.get_history("alice")
    bob_history_before = service.get_history("bob")

    with pytest.raises(InsufficientFundsError):
        service.transfer("alice", "bob", Decimal("5.00"))

    assert service.get_balance("alice") == Decimal("4.00")
    assert service.get_balance("bob") == Decimal("0.00")
    assert service.get_history("alice") == alice_history_before
    assert service.get_history("bob") == bob_history_before


def test_invalid_operation_never_appears_in_history() -> None:
    service = WalletService()
    service.create_wallet("alice")

    with pytest.raises(InvalidAmountError):
        service.deposit("alice", Decimal("0.001"))

    assert service.get_history("alice") == ()


def test_wallets_do_not_share_history_storage() -> None:
    service = WalletService()
    service.create_wallet("alice")
    service.create_wallet("bob")

    service.deposit("alice", Decimal("1.00"))

    assert len(service.get_history("alice")) == 1
    assert service.get_history("bob") == ()
