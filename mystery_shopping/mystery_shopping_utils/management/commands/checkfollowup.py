from django.core.management.base import BaseCommand
from django.utils import timezone

from mystery_shopping.mail_service.detractors_mail import send_notification_email_for_follow_up
from mystery_shopping.respondents.models import RespondentCase


class Command(BaseCommand):

    def handle(self, *args, **options):
        today = timezone.now()
        cases = RespondentCase.objects.filter(follow_up_date=today)
        for case in cases:
            send_notification_email_for_follow_up(case)
