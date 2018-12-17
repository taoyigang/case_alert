from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from cases.models import Case
import datetime


class Command(BaseCommand):
	help = 'Closes the specified poll for voting'

	def handle(self, *args, **options):
		date_today = timezone.now().today()
		today_min = datetime.datetime.combine(date_today, datetime.time.min)
		today_max = datetime.datetime.combine(date_today, datetime.time.max)
		cases = Case.objects.filter(deadline__range=(today_min, today_max)).all()
		for case in cases:
			subject = 'Case {} deadline alert'.format(case.case_id)
			content = 'Hello {}:\n\n    Today({}) is the deadline of case {}.\n    Please be ready to finish it.\n\nRegards'.format(
				case.user, case.deadline.strftime("%Y-%m-%d"), case.case_id)
			from_email = settings.EMAIL_HOST_USER or 'test@gmail.com'
			recipient = [case.user.email]
			send_mail(subject, content, from_email, recipient)
