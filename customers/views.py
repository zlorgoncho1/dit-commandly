from django.shortcuts import render
from .views.customer import (
    customer_list, customer_detail, customer_create,
    customer_update, customer_delete, customer_toggle_status,
    customer_quick_search
)

__all__ = [
    'customer_list', 'customer_detail', 'customer_create',
    'customer_update', 'customer_delete', 'customer_toggle_status',
    'customer_quick_search'
]
