from django.shortcuts import render
from .views.payment import (
    payment_list, payment_detail, payment_create,
    payment_update, payment_delete, payment_update_status,
    payment_mark_completed, payment_mark_failed, payment_mark_cancelled,
    payment_quick_search
)

__all__ = [
    'payment_list', 'payment_detail', 'payment_create',
    'payment_update', 'payment_delete', 'payment_update_status',
    'payment_mark_completed', 'payment_mark_failed', 'payment_mark_cancelled',
    'payment_quick_search'
]

# Create your views here.
