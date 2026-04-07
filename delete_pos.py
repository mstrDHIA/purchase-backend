import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purchase_backend.settings')
django.setup()

from purchase_order.models import PurchaseOrder

# Delete all PurchaseOrder records
count_before = PurchaseOrder.objects.count()
print(f'PurchaseOrders avant suppression: {count_before}')

PurchaseOrder.objects.all().delete()

count_after = PurchaseOrder.objects.count()
print(f'PurchaseOrders après suppression: {count_after}')
print('✓ Tous les PurchaseOrders ont été supprimés')
