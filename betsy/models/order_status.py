from enum import Enum

class OrderStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    @staticmethod
    def all():
        return [status.value for status in list(OrderStatus)]
