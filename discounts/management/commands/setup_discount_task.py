from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = "Set up periodic tasks for updating discounts"

    def handle(self, *args, **kwargs):
        # Create or get the crontab schedule for 12:00 AM daily
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="0",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        # Create the periodic task
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name="Update Discounts",
            task="discounts.tasks.update_discounts",
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Periodic task 'Update Discounts' created successfully."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Periodic task 'Update Discounts' already exists.")
            )
