# Vues pour l'application orders
from .order import (
    OrderListView, OrderCreateView, OrderDetailView, OrderUpdateView, OrderDeleteView, 
    OrderStatusUpdateView, OrderQuickSearchView, OrderItemCreateView, OrderItemUpdateView, OrderItemDeleteView
)

__all__ = [
    'OrderListView', 'OrderCreateView', 'OrderDetailView', 'OrderUpdateView', 'OrderDeleteView', 
    'OrderStatusUpdateView', 'OrderQuickSearchView', 'OrderItemCreateView', 'OrderItemUpdateView', 'OrderItemDeleteView'
]
