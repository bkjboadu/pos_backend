from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = "Set up periodic tasks for updating promotions"

    def handle(self, *args, **kwargs):
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="0",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name="Update Promotions",
            task="promotions.tasks.update_promotions",
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Periodic task 'Update Promotions' created successfully."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Periodic task 'Update Promotions' already exists.")
            )
