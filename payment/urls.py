from django.urls import path
from .views import (
    PayCashView,
    StripePaymentIntentView,
    StripePaymentConfirmView,
    ReceiptPDFView,
    PaymentView,
    PaymentDetailView
)

urlpatterns = [
    path("",PaymentView.as_view(), name='payment-view'),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail-view"),
    path(
        "stripe-confirm-payment/",
        StripePaymentConfirmView.as_view(),
        name="stripe-payment-success",
    ),
    path(
        "stripe-create-payment-intent/",
        StripePaymentIntentView.as_view(),
        name="stripe-payment-intent",
    ),
    path("pay-with-cash/", PayCashView.as_view(), name="pay-with-cash"),
    path(
        "receipts/<int:transaction_id>/", ReceiptPDFView.as_view(), name="get-receipt"
    ),
]
