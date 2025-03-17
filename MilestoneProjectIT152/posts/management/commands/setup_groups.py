from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

# user = User.objects.create_user(username='new_admin', password='secure_pass123')

class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **kwargs):

        admin_group, created = Group.objects.get_or_create(name='new_admin')

        try:
            user = User.objects.get(username='new_admin')
            user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Admin user added to admin group'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found'))