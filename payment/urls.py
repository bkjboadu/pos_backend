from django.urls import path
from .views import (
    PayCashView,
    StripePaymentIntentView,
    StripePaymentConfirmView
)

urlpatterns = [
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
]
