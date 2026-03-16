import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purchase_backend.settings')
django.setup()

from django.test import RequestFactory
from statistic.views import total_price_dinar_view
import json

factory = RequestFactory()

print("=" * 100)
print("Testing /stats/po/total-price-dinar/ endpoint")
print("=" * 100)

request = factory.get('/stats/po/total-price-dinar/')
response = total_price_dinar_view(request)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Data: {response.data}")
print(f"Response Type: {type(response.data)}")

# Verify the value is a number
if 'total_price_dinar' in response.data:
    total = response.data['total_price_dinar']
    print(f"\nTotal Price Dinar: {total}")
    print(f"Type: {type(total).__name__}")
    print(f"Is float/int: {isinstance(total, (int, float))}")
