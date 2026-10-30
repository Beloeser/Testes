"""Immutable value objects used in wallet operation histories."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class OperationType(StrEnum):
    """Kinds of operation that can change a wallet balance."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


@dataclass(frozen=True, slots=True)
class Operation:
    """A single immutable entry in a wallet history."""

    type: OperationType
    amount: Decimal
    balance_after: Decimal
    counterparty_wallet_id: str | None = None
    transfer_id: UUID | None = None
