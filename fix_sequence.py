import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purchase_backend.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Get the maximum ID
cursor.execute("SELECT MAX(id) FROM purchase_order_purchaseorder;")
max_id = cursor.fetchone()[0]

if max_id:
    print(f'Max ID in database: {max_id}')
    # Reset sequence to max_id + 1
    cursor.execute(f"SELECT setval('purchase_order_purchaseorder_id_seq', {max_id + 1});")
    print(f'Sequence reset to: {max_id + 1}')
else:
    print('No records in table')
    cursor.execute("SELECT setval('purchase_order_purchaseorder_id_seq', 1);")
    print('Sequence reset to: 1')
