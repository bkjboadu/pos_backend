from django.urls import path
from . import views

urlpatterns = [
    path(
        "stripe-confirm-payment/",
        views.StripePaymentConfirmView.as_view(),
        name="stripe-payment-success",
    ),
    path(
        "stripe-create-payment-intent/",
        views.StripePaymentIntentView.as_view(),
        name="stripe-payment-intent",
    ),
]
