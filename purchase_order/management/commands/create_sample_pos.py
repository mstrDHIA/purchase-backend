from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Max
from django.contrib.auth import get_user_model
import random
from datetime import timedelta

from purchase_order.models import PurchaseOrder
from purchase_request.models import PurchaseRequest


class Command(BaseCommand):
    help = 'Create varied sample PurchaseRequest and PurchaseOrder records for local testing (departments, requesters, categories, suppliers, archived/rejected)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Number of POs to create')

    def handle(self, *args, **options):
        User = get_user_model()
        count = options['count']

        # create/get users to act as requesters
        usernames = ['admin', 'supervisor', 'user1', 'user2', 'user3']
        users = []
        for username in usernames:
            user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            users.append(user)

        # departments
        try:
            from department.models import Department
            # Assign departments to users
            dept_names = ['HR', 'IT', 'Finance', 'Operations']
            depts = []
            for n in dept_names:
                d, _ = Department.objects.get_or_create(name=n)
                depts.append(d)
            # Assign departments to users if not already set
            for user in users:
                if not hasattr(user, 'dep_id') or user.dep_id is None:
                    user.dep_id = random.choice(depts)
                    user.save()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not set user departments: {e}'))
            depts = [None]

        # ensure there are some reject reasons
        try:
            from reject_reasons.models import RejectReason
            if not RejectReason.objects.exists():
                RejectReason.objects.create(name='Incomplete')
                RejectReason.objects.create(name='Budget')
            reject_reasons = list(RejectReason.objects.all())
        except Exception:
            reject_reasons = []

        # lists for product metadata
        sample_suppliers = ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D']
        sample_categories = ['IT', 'Office', 'Maintenance', 'Facilities']
        sample_subcats = ['Hardware', 'Software', 'Consumables', 'Services']
        sample_families = ['Computer', 'Office Equipment', 'Cleaning', 'Building']
        sample_subfamilies = ['Desktop', 'Laptop', 'Printer', 'Monitor', 'Desk', 'Chair', 'Broom', 'Bucket', 'Door', 'Window']

        # determine next id start (PurchaseOrder.id is IntegerField PK)
        max_po_id = PurchaseOrder.objects.aggregate(max_id=Max('id'))['max_id'] or 0
        created_prs = 0
        created_pos = 0
        now = timezone.now()

        # Create PurchaseRequests and corresponding PurchaseOrders
        for i in range(1, count + 1):
            next_id = max_po_id + i
            requester = random.choice(users)
            dept = random.choice(depts)
            supplier = random.choice(sample_suppliers)
            category = random.choice(sample_categories)
            subcat = random.choice(sample_subcats)
            family = random.choice(sample_families)
            subfamily = random.choice(sample_subfamilies)

            title = f"Sample PO {next_id}"
            products = [{
                'name': f'Product {i}',
                'category': category,
                'category_name': category,
                'subcategory': subcat,
                'subcategory_name': subcat,
                'family': family,
                'family_name': family,
                'subfamily': subfamily,
                'subfamily_name': subfamily,
                'supplier': supplier,
                'supplier_name': supplier,
                'quantity': random.randint(1, 20),
            }]

            # some archived, some not
            is_archived = (i % 5 == 0)  # ~20% archived

            # some rejected (~30%)
            statuss = 'rejected' if i % 3 == 0 else 'pending'

            # spread created_at across past 120 days
            created_at = now - timedelta(days=random.randint(0, 120))

            # Create PurchaseRequest first
            try:
                pr = PurchaseRequest.objects.create(
                    title=f"PR for {title}",
                    description='Auto-generated sample PR for testing',
                    requested_by=requester,  # PR creator - key for requester grouping
                    products=products,
                    status=random.choice(['pending', 'approved', 'transformed']),
                    is_archived=is_archived,
                    priority=random.choice(['low', 'medium', 'high']),
                    created_at=created_at,
                )
                created_prs += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not create PR for PO {next_id}: {e}'))
                pr = None

            # Create PurchaseOrder and link to PR
            po = PurchaseOrder(
                id=next_id,
                title=title,
                description='Auto-generated sample PO for testing filters',
                requested_by_user=requester,
                products=products,
                is_archived=is_archived,
                department=dept,
                statuss=statuss,  # Set rejected status
                created_at=created_at,
                purchase_request=pr,  # Link to PR
            )

            try:
                po.save()
                created_pos += 1
            except Exception as e:
                # skip problematic saves but continue
                self.stdout.write(self.style.WARNING(f'Could not create PO {next_id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Created {created_prs} PurchaseRequests and {created_pos} sample PurchaseOrders'))
