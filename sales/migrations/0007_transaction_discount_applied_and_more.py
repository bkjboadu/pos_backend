# Generated by Django 5.1.1 on 2025-01-09 17:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discounts", "0002_rename_name_discount_code"),
        ("sales", "0006_remove_transaction_payment_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="discount_applied",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="transactions",
                to="discounts.discount",
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="promotion_applied",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="transactions",
                to="discounts.promotion",
            ),
        ),
    ]