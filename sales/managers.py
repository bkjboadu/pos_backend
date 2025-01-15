from django.db import models
from django.db.models import Sum, Count


class TransactionQuerySet(models.QuerySet):
    def total_sales(self, start_date=None, end_date=None):
        query = self.filter(created_at__range=(start_date, end_date)) if start_date and end_date else self
        return query.aggregate(total=Sum('total_amount'))['total'] or 0

    def sales_by_product(self, product_id=None):
        query = self.filter(items__product_id=product_id) if product_id else self
        return query.values("items__product__name").annotate(
            total_quantity=Sum('items__quantity'),
            total_sales=Sum("items__total_amount")
        )

class TransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)

    def total_sales(self, *args, **kwargs):
        return self.get_queryset().total_sales(*args, **kwargs)

    def sales_by_product(self, *args, **kwargs):
        return self.get_queryset().sales_by_product(*args, **kwargs)
