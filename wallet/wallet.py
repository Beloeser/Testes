"""Wallet entity and its balance-changing domain rules."""

from decimal import Decimal, InvalidOperation
from uuid import UUID, uuid4

from wallet.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidTransferError,
    InvalidWalletIdError,
)
from wallet.models import Operation, OperationType

_CENT = Decimal("0.01")
_ZERO = Decimal("0.00")


def validate_wallet_id(wallet_id: str) -> str:
    """Return a valid wallet id or raise a domain error."""
    if (
        not isinstance(wallet_id, str)
        or not wallet_id
        or wallet_id != wallet_id.strip()
    ):
        raise InvalidWalletIdError(
            "Wallet id must be a non-empty string without surrounding whitespace."
        )
    return wallet_id


def validate_amount(amount: Decimal) -> Decimal:
    """Return a value normalized to cents or raise a domain error."""
    if not isinstance(amount, Decimal):
        raise InvalidAmountError("Amount must be a Decimal.")
    if not amount.is_finite() or amount <= _ZERO:
        raise InvalidAmountError("Amount must be finite and greater than zero.")

    try:
        normalized = amount.quantize(_CENT)
    except InvalidOperation as error:
        raise InvalidAmountError("Amount must be representable in cents.") from error

    if normalized != amount:
        raise InvalidAmountError("Amount cannot have fractions of a cent.")
    return normalized


class Wallet:
    """An in-memory wallet with an immutable public history."""

    def __init__(self, wallet_id: str) -> None:
        self._id = validate_wallet_id(wallet_id)
        self._balance = _ZERO
        self._history: list[Operation] = []

    @property
    def id(self) -> str:
        """The wallet identifier."""
        return self._id

    @property
    def balance(self) -> Decimal:
        """The current balance."""
        return self._balance

    @property
    def history(self) -> tuple[Operation, ...]:
        """A read-only snapshot of operations in chronological order."""
        return tuple(self._history)

    def deposit(self, amount: Decimal) -> Operation:
        """Add a positive amount to this wallet."""
        normalized = validate_amount(amount)
        self._balance += normalized
        operation = Operation(
            type=OperationType.DEPOSIT,
            amount=normalized,
            balance_after=self._balance,
        )
        self._history.append(operation)
        return operation

    def withdraw(self, amount: Decimal) -> Operation:
        """Remove an amount when enough balance is available."""
        normalized = validate_amount(amount)
        self._ensure_sufficient_funds(normalized)
        self._balance -= normalized
        operation = Operation(
            type=OperationType.WITHDRAWAL,
            amount=normalized,
            balance_after=self._balance,
        )
        self._history.append(operation)
        return operation

    def transfer_to(
        self, destination: "Wallet", amount: Decimal
    ) -> tuple[Operation, Operation]:
        """Atomically transfer an amount to a different wallet."""
        if not isinstance(destination, Wallet) or destination.id == self.id:
            raise InvalidTransferError(
                "Source and destination must be different valid wallets."
            )

        normalized = validate_amount(amount)
        self._ensure_sufficient_funds(normalized)
        transfer_id = uuid4()

        self._balance -= normalized
        destination._balance += normalized

        outgoing = self._transfer_operation(
            type=OperationType.TRANSFER_OUT,
            amount=normalized,
            counterparty_wallet_id=destination.id,
            transfer_id=transfer_id,
        )
        incoming = destination._transfer_operation(
            type=OperationType.TRANSFER_IN,
            amount=normalized,
            counterparty_wallet_id=self.id,
            transfer_id=transfer_id,
        )
        self._history.append(outgoing)
        destination._history.append(incoming)
        return outgoing, incoming

    def _ensure_sufficient_funds(self, amount: Decimal) -> None:
        if amount >= self._balance:
            raise InsufficientFundsError(
                f"Wallet {self.id!r} does not have enough balance."
            )

    def _transfer_operation(
        self,
        *,
        type: OperationType,
        amount: Decimal,
        counterparty_wallet_id: str,
        transfer_id: UUID,
    ) -> Operation:
        return Operation(
            type=type,
            amount=amount,
            balance_after=self._balance,
            counterparty_wallet_id=counterparty_wallet_id,
            transfer_id=transfer_id,
        )
