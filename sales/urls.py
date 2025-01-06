from django.urls import path
from .views import TransactionItemDetailView, TransactionView, TransactionItemView, TransactionDetailView, TransactionItemDetailView

urlpatterns = [
    path('transactions/',TransactionView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/',TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions-items/', TransactionItemView.as_view(), name='transaction-item-list'),
    path('transactions-items/<int:pk>/', TransactionItemDetailView.as_view(), name='transaction-item-detail')
]
