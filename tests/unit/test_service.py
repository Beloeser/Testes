from decimal import Decimal

import pytest

from wallet import (
    InvalidWalletIdError,
    WalletAlreadyExistsError,
    WalletNotFoundError,
    WalletService,
)


def test_create_wallet_and_query_balance() -> None:
    service = WalletService()

    wallet = service.create_wallet("alice")

    assert wallet.id == "alice"
    assert service.get_balance("alice") == Decimal("0.00")


def test_create_wallet_rejects_duplicate_without_replacing_original() -> None:
    service = WalletService()
    original = service.create_wallet("alice")
    service.deposit("alice", Decimal("3.00"))

    with pytest.raises(WalletAlreadyExistsError):
        service.create_wallet("alice")

    assert service.get_balance("alice") == Decimal("3.00")
    assert service.get_history("alice") == original.history


@pytest.mark.parametrize("wallet_id", ["", " alice", "alice "])
def test_service_rejects_invalid_wallet_id(wallet_id: str) -> None:
    service = WalletService()

    with pytest.raises(InvalidWalletIdError):
        service.get_balance(wallet_id)


@pytest.mark.parametrize(
    ("operation", "arguments"),
    [
        ("get_balance", ("missing",)),
        ("deposit", ("missing", Decimal("1.00"))),
        ("withdraw", ("missing", Decimal("1.00"))),
        ("get_history", ("missing",)),
    ],
)
def test_operations_reject_unknown_wallet(
    operation: str, arguments: tuple[object, ...]
) -> None:
    service = WalletService()

    with pytest.raises(WalletNotFoundError):
        getattr(service, operation)(*arguments)
