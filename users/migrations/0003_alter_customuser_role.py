# Generated by Django 5.1.1 on 2025-01-02 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_customuser_company_alter_customuser_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("company_admin", "Company Admin"),
                    ("cashier", "Cashier"),
                    ("manager", "Manager"),
                ],
                default=None,
                max_length=50,
                null=True,
            ),
        ),
    ]