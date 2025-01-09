from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product

@receiver(post_save, sender=Product)
def handle_product_save(sender, instance, created, **kwargs):
    if created:
        print(f"Product added: {instance.name}")
    else:
        print(f"Product updated: {instance.name}")
