from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from cases.models import Case


class Command(BaseCommand):
	help = 'Closes the specified poll for voting'

	def add_arguments(self, parser):
		parser.add_argument('case_id', nargs='+', type=int)

	def handle(self, *args, **options):
		for case_id in options['case_id']:
			try:
				case = Case.objects.get(pk=case_id)
			except Case.DoesNotExist:
				raise CommandError('Case "%s" does not exist' % case_id)
			subject = 'Case {} deadline alert'.format(case.case_id)
			content = 'Hello {}:\n     Today is the deadline of case {}.\n   Please be ready to finish it.'.format(case.user, case.case_id)
			from_email = settings.EMAIL_HOST_USER or 'test@gmail.com'
			recipient = [case.user.email]
			send_mail(subject, content, from_email, recipient)
