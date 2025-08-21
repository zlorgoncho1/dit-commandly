from django.shortcuts import render
from .views.order import (
    order_list, order_detail, order_create,
    order_update, order_delete, order_update_status,
    order_item_create, order_item_update, order_item_delete,
    order_quick_search
)

__all__ = [
    'order_list', 'order_detail', 'order_create',
    'order_update', 'order_delete', 'order_update_status',
    'order_item_create', 'order_item_update', 'order_item_delete',
    'order_quick_search'
]
