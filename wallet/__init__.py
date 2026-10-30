"""Public API for the Wallet educational project."""

from wallet.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidTransferError,
    InvalidWalletIdError,
    WalletAlreadyExistsError,
    WalletError,
    WalletNotFoundError,
)
from wallet.models import Operation, OperationType
from wallet.service import WalletService
from wallet.wallet import Wallet

__all__ = [
    "InsufficientFundsError",
    "InvalidAmountError",
    "InvalidTransferError",
    "InvalidWalletIdError",
    "Operation",
    "OperationType",
    "Wallet",
    "WalletAlreadyExistsError",
    "WalletError",
    "WalletNotFoundError",
    "WalletService",
]
