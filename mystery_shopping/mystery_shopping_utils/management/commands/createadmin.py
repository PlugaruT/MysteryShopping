from django.core.management.base import BaseCommand

from mystery_shopping.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email="iulian.gulea@sparklabs.md").exists():
            User.objects.create_superuser('iulian.gulea', "iulian.gulea@sparklabs.md", "gulea")
