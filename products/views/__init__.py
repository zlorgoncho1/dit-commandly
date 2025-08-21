# Vues pour l'application products
from .product import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductActivateView,
    ProductDeactivateView,
    ProductStockUpdateView,
    ProductToggleStatusView,
    ProductPriceUpdateView,
    ProductQuickSearchView,
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
)

__all__ = [
    # CBV
    'ProductListView',
    'ProductDetailView',
    'ProductCreateView',
    'ProductUpdateView',
    'ProductDeleteView',
    'ProductActivateView',
    'ProductDeactivateView',
    'ProductStockUpdateView',
    'ProductToggleStatusView',
    'ProductPriceUpdateView',
    'ProductQuickSearchView',
    'CategoryListView',
    'CategoryDetailView',
    'CategoryCreateView',
    'CategoryUpdateView',
    'CategoryDeleteView',
]
