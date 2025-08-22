# Vues pour l'application customers
from .customer import (
    CustomerListView, CustomerCreateView, CustomerDetailView, CustomerUpdateView, CustomerDeleteView,
    CustomerToggleStatusView, CustomerQuickSearchView
)

__all__ = [
    'CustomerListView', 'CustomerCreateView', 'CustomerDetailView', 'CustomerUpdateView', 'CustomerDeleteView',
    'CustomerToggleStatusView', 'CustomerQuickSearchView'
]
