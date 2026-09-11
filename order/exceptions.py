class OrderNotFoundError(Exception):
    pass

class AmountExceededError(Exception):
    pass

class InvalidOrderStatusError(Exception):
    pass

class PaymentNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class ProductNotFoundError(Exception):
    pass

class UserExistError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

class OrderAccessDeniedError(Exception):
    pass

class InsufficientStockError(Exception):
    pass