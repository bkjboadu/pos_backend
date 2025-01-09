from celery import shared_task
from django.utils.timezone import now
from .models import Discount, Promotion

@shared_task
def update_discounts():
    discounts = Discount.objects.filter(is_active=True, end_date__lt=now())
    discounts.update(is_active=False)
    return f"{discounts.count()} discounts deactivated."


@shared_task
def update_promotions():
    promotions = Promotion.objects.filter(is_active=True, end_date__lt=now())
    promotions.update(is_active=False)
    return f"{promotions.count()} promotion deactivated"
