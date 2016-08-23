from django.core.management.base import BaseCommand

from mystery_shopping.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email="mystery.user@sparklabs.md").exists():
            User.objects.create_superuser('mystery.user', "mystery.user@sparklabs.md", "mystery")
