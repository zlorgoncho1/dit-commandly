from django.shortcuts import render
from .views.invoice import (
    invoice_list, invoice_detail, invoice_create,
    invoice_update, invoice_delete, invoice_update_status,
    invoice_generate_pdf, invoice_send_email, invoice_quick_search
)

__all__ = [
    'invoice_list', 'invoice_detail', 'invoice_create',
    'invoice_update', 'invoice_delete', 'invoice_update_status',
    'invoice_generate_pdf', 'invoice_send_email', 'invoice_quick_search'
]

# Create your views here.
