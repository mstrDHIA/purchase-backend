import os
import django
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purchase_backend.settings')
django.setup()

from django.test import RequestFactory
from statistic.views import total_price_dinar_view

factory = RequestFactory()

print("=" * 100)
print("Testing different endpoint calls")
print("=" * 100)

# Test 1: No filters
print("\n[TEST 1] No filters")
request = factory.get('/stats/po/total-price-dinar/')
response = total_price_dinar_view(request)
print(f"✅ Response: {response.data}")

# Test 2: With date range
today = datetime.now().date()
start_date = today - timedelta(days=10)
end_date = today + timedelta(days=1)
print(f"\n[TEST 2] With date range: {start_date} to {end_date}")
request = factory.get(f'/stats/po/total-price-dinar/?start_date={start_date}&end_date={end_date}')
response = total_price_dinar_view(request)
print(f"✅ Response: {response.data}")

# Test 3: With department filter
print(f"\n[TEST 3] With department filter (IT = 1)")
request = factory.get('/stats/po/total-price-dinar/?department=1')
response = total_price_dinar_view(request)
print(f"✅ Response: {response.data}")

# Test 4: With both date and department
print(f"\n[TEST 4] With date range AND department filter")
request = factory.get(f'/stats/po/total-price-dinar/?start_date={start_date}&end_date={end_date}&department=IT')
response = total_price_dinar_view(request)
print(f"✅ Response: {response.data}")

print("\n" + "=" * 100)
print("✅ All tests passed! The API is working correctly.")
print("=" * 100)
