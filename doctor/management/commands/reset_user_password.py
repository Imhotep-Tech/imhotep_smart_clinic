from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Resets password and activates email_verify for a given username.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to update')
        parser.add_argument('password', type=str, help='New password')

    def handle(self, *args, **options):
        username = options['username']
        new_password = options['password']

        user = User.objects.filter(username=username).first()
        if not user:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found."))
            return

        user.set_password(new_password)
        user.email_verify = True
        user.is_active = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully updated password and activated user '{username}'!"))
