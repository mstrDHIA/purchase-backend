from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from purchase_request.models import PurchaseRequest   # adjust import path if your app/model name differs
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Archives orders older than a given number of days (default: 30)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after which an request becomes archived (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show how many would be archived without updating DB'
        )

    def handle(self, *args, **options):
        days = options.get('days', 30)
        dry_run = options.get('dry_run', False)
        cutoff = timezone.now() - timedelta(days=days)

        qs = PurchaseRequest.objects.filter(is_archived=False, created_at__lt=cutoff)
        count = qs.count()

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"DRY RUN: {count} requests WOULD be archived (older than {days} days)."
            ))
            return

        updated = qs.update(is_archived=True)
        self.stdout.write(self.style.SUCCESS(
            f"{updated} requests archived (created before {cutoff})."
        ))
        logger.info("Archived %d requests older than %d days", updated, days)



# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from datetime import timedelta
# from purchase_order.models import PurchaseOrder
# import logging

# logger = logging.getLogger(__name__)

# class Command(BaseCommand):
#     help = 'Archives orders older than 30 days'

#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--days',
#             type=int,
#             default=30,
#             help='Number of days after which an order becomes archived (default: 30)'
#         )
#         parser.add_argument(
#             '--dry-run',
#             action='store_true',
#             help='Show how many would be archived without updating DB'
#         )

#     def handle(self, *args, **options):
#         days = options['days']
#         dry_run = options['dry_run']
#         cutoff = timezone.now() - timedelta(days=days)
#         qs = PurchaseOrder.objects.filter(is_archived=False, created_at__lt=cutoff)

#         count = qs.count()
#         if dry_run:
#             self.stdout.write(self.style.WARNING(f'DRY RUN: {count} orders WOULD be archived (older than {days} days).'))
#             return

#         updated = qs.update(is_archived=True)
#         self.stdout.write(self.style.SUCCESS(f'{updated} orders archived (created before {cutoff}).'))
#         logger.info('Archived %d orders older than %d days', updated, days)
