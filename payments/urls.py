from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
]
