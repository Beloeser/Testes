"""Domain exceptions raised by the wallet system."""


class WalletError(Exception):
    """Base class for all expected wallet errors."""


class InvalidWalletIdError(WalletError):
    """Raised when a wallet identifier is not valid."""


class WalletAlreadyExistsError(WalletError):
    """Raised when a wallet identifier is already registered."""


class WalletNotFoundError(WalletError):
    """Raised when an operation references an unknown wallet."""


class InvalidAmountError(WalletError):
    """Raised when a monetary value is not valid."""


class InsufficientFundsError(WalletError):
    """Raised when a debit is greater than the available balance."""


class InvalidTransferError(WalletError):
    """Raised when a transfer is internally inconsistent."""
