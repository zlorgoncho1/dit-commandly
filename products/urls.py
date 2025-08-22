from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('toggle-status/<int:pk>/', views.ProductToggleStatusView.as_view(), name='product_toggle_status'),
    path('quick-search/', views.ProductQuickSearchView.as_view(), name='product_quick_search'),
    path('activate/<int:pk>/', views.ProductActivateView.as_view(), name='product_activate'),
    path('deactivate/<int:pk>/', views.ProductDeactivateView.as_view(), name='product_deactivate'),
    path('stock-update/<int:pk>/', views.ProductStockUpdateView.as_view(), name='product_stock_update'),
    path('price-update/<int:pk>/', views.ProductPriceUpdateView.as_view(), name='product_price_update'),
]
