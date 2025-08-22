from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    path('<int:pk>/toggle-status/', views.CustomerToggleStatusView.as_view(), name='customer_toggle_status'),
    path('quick-search/', views.CustomerQuickSearchView.as_view(), name='customer_quick_search'),
]
