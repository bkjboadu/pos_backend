# Generated by Django 5.1.1 on 2025-01-18 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0002_alter_payment_transaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="card_payment",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="cash_payment",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="payment_method",
            field=models.CharField(
                choices=[("cash", "Cash"), ("card", "Card"), ("Split", "Split")],
                max_length=10,
            ),
        ),
    ]
