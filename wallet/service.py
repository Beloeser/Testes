"""Application service that manages wallets in memory."""

from decimal import Decimal

from wallet.exceptions import WalletAlreadyExistsError, WalletNotFoundError
from wallet.models import Operation
from wallet.wallet import Wallet, validate_wallet_id


class WalletService:
    """Create wallets and coordinate their operations."""

    def __init__(self) -> None:
        self._wallets: dict[str, Wallet] = {}

    def create_wallet(self, wallet_id: str) -> Wallet:
        """Create an empty wallet with a unique identifier."""
        valid_id = validate_wallet_id(wallet_id)
        if valid_id in self._wallets:
            raise WalletAlreadyExistsError(
                f"Wallet {valid_id!r} already exists."
            )

        wallet = Wallet(valid_id)
        self._wallets[valid_id] = wallet
        return wallet

    def get_balance(self, wallet_id: str) -> Decimal:
        """Return the current balance of an existing wallet."""
        return self._get_wallet(wallet_id).balance

    def deposit(self, wallet_id: str, amount: Decimal) -> Operation:
        """Deposit money in an existing wallet."""
        return self._get_wallet(wallet_id).deposit(amount)

    def withdraw(self, wallet_id: str, amount: Decimal) -> Operation:
        """Withdraw money from an existing wallet."""
        return self._get_wallet(wallet_id).withdraw(amount)

    def transfer(
        self, source_wallet_id: str, destination_wallet_id: str, amount: Decimal
    ) -> tuple[Operation, Operation]:
        """Transfer money between two existing wallets."""
        source = self._get_wallet(source_wallet_id)
        destination = self._get_wallet(destination_wallet_id)
        return source.transfer_to(destination, amount)

    def get_history(self, wallet_id: str) -> tuple[Operation, ...]:
        """Return a read-only snapshot of a wallet history."""
        return self._get_wallet(wallet_id).history

    def _get_wallet(self, wallet_id: str) -> Wallet:
        valid_id = validate_wallet_id(wallet_id)
        try:
            return self._wallets[valid_id]
        except KeyError as error:
            raise WalletNotFoundError(
                f"Wallet {valid_id!r} was not found."
            ) from error
