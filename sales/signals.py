from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction, TransactionItem


@receiver(post_save, sender=Transaction)
def handle_transaction_save(sender, instance, created, **kwargs):
    if created:
        print(f"Transaction added: {instance.id}")
    else:
        print(f"Transaction updated: {instance.id}")


@receiver(post_save, sender=TransactionItem)
def handle_transactionitem_save(sender, instance, created, **kwargs):
    if created:
        print(f"TransactionItem added: {instance.id}")
    else:
        print(f"TransactionItem updated: {instance.id}")
