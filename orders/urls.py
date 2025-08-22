from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order_update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('quick-search/', views.OrderQuickSearchView.as_view(), name='order_quick_search'),
    path('<int:pk>/items/create/', views.OrderItemCreateView.as_view(), name='order_item_create'),
    path('<int:pk>/items/<int:item_pk>/edit/', views.OrderItemUpdateView.as_view(), name='order_item_update'),
    path('<int:pk>/items/<int:item_pk>/delete/', views.OrderItemDeleteView.as_view(), name='order_item_delete'),
]
