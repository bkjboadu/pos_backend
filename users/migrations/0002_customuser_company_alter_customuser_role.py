# Generated by Django 5.1.1 on 2025-01-01 18:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0002_company_country_alter_branch_unique_together"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="company",
            field=models.ForeignKey(
                blank=True,
                help_text="The company this user is associated with. Null for system-wide superusers.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to="companies.company",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[
                    ("company_admin", "Company Admin"),
                    ("cashier", "Cashier"),
                    ("manager", "Manager"),
                ],
                default="cashier",
                max_length=50,
            ),
        ),
    ]