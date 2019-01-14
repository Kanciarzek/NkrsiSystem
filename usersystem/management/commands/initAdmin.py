import os
from django.core.management import BaseCommand
from usersystem.models import User


class Command(BaseCommand):

    help = 'Creates superuser where no users is present in database.'

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            email = os.environ['SUPER_EMAIL']
            password = os.environ['SUPER_PASSWORD']
            print('Creating superuser account for %s' % email)
            User.objects.create_superuser(email=email, password=password)
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
