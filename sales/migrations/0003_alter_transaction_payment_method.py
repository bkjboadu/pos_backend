# Generated by Django 5.1.1 on 2025-01-08 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0002_transaction_created_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[("cash", "Cash"), ("card", "Card")],
                max_length=10,
                null=True,
            ),
        ),
    ]
