from rest_framework.exceptions import APIException
from rest_framework import status

class AppBaseException(APIException):
    """
    Base class for all custom business logic exceptions.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'INTERNAL_SERVER_ERROR'
    default_message = "An unexpected server error occurred."

    def __init__(self, message=None, details=None):
        self.message = message or self.default_message
        self.details = details
        # Pass to APIException so DRF internals also see it if needed
        super().__init__(detail=self.message, code=self.error_code)


# --- CORE / GLOBAL ---
class ResourceNotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'RESOURCE_NOT_FOUND'
    default_message = "The requested resource was not found."

class InvalidRequestStateError(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INVALID_REQUEST_STATE'
    default_message = "The system state does not allow this operation."


# --- AUTHENTICATION ---
class InvalidInitDataError(AppBaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 'AUTH_INVALID_INIT_DATA'
    default_message = "Invalid or missing Telegram initData."

class InitDataExpiredError(AppBaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 'AUTH_INIT_DATA_EXPIRED'
    default_message = "Telegram initData has expired."


# --- CART ---
class CartEmptyError(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'CART_IS_EMPTY'
    default_message = "The requested cart is empty."

class CartItemNotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'CART_ITEM_NOT_FOUND'
    default_message = "The specified item is not in the cart."

class InvalidCartQuantityError(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'CART_INVALID_QUANTITY'
    default_message = "Invalid quantity specified for cart item."


# --- ORDERS ---
class OrderNotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'ORDER_NOT_FOUND'
    default_message = "The specified order was not found."

class OrderAlreadyProcessingError(AppBaseException):
    status_code = status.HTTP_409_CONFLICT
    error_code = 'ORDER_ALREADY_PROCESSING'
    default_message = "Order creation blocked. Active order already in progress."

class OrderStatusConflictError(AppBaseException):
    status_code = status.HTTP_409_CONFLICT
    error_code = 'ORDER_STATUS_CONFLICT'
    default_message = "Cannot perform this action due to the current order status."


# --- CATALOG ---
class ProductNotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'PRODUCT_NOT_FOUND'
    default_message = "The requested product does not exist."

class ProductOutOfStockError(AppBaseException):
    status_code = status.HTTP_409_CONFLICT
    error_code = 'PRODUCT_OUT_OF_STOCK'
    default_message = "The specific product or quantity is out of stock."

class CategoryNotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'CATEGORY_NOT_FOUND'
    default_message = "The requested category does not exist."


# --- CLIENTS ---
class ClientNotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'CLIENT_NOT_FOUND'
    default_message = "The specified client profile was not found."

class ClientBannedError(AppBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'CLIENT_BANNED'
    default_message = "This client has been restricted from the platform."


# --- FAQ & BROADCASTS ---
class FAQNotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'FAQ_NOT_FOUND'
    default_message = "FAQ item not found."

class BroadcastFailedError(AppBaseException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'BROADCAST_FAILED'
    default_message = "Failed to process the broadcast operation."


# --- BOT SETTINGS ---
class BotConfigDeletionForbiddenError(AppBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'CONFIG_DELETION_FORBIDDEN'
    default_message = "This core configuration cannot be deleted."
