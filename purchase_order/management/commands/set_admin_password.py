from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Set admin user password to provided value (default: admin)'

    def add_arguments(self, parser):
        parser.add_argument('--password', type=str, default='admin', help='Password to set for admin')

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        pwd = options['password']
        u = User.objects.filter(username='admin').first()
        if u:
            u.set_password(pwd)
            u.save()
            self.stdout.write(self.style.SUCCESS(f"Password for 'admin' set to '{pwd}'"))
        else:
            try:
                User.objects.create_superuser('admin', 'admin@example.com', pwd)
                self.stdout.write(self.style.SUCCESS("Superuser 'admin' created"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Could not create admin: {e}"))
