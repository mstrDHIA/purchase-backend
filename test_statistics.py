#!/usr/bin/env python
"""
Script de test pour valider les endpoints statistiques
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purchase_backend.settings')
django.setup()

from django.test import RequestFactory
from statistic.views import POTotalsView, PORejectionRateView, total_price_dinar_view
from purchase_order.models import PurchaseOrder

# Initialiser le factory
factory = RequestFactory()

print("=" * 80)
print("TEST 1: POTotalsView avec group_by=summary (sans filtres)")
print("=" * 80)
request = factory.get('/stats/po/totals/?group_by=summary')
view = POTotalsView.as_view()
response = view(request)
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
print()

print("=" * 80)
print("TEST 2: POTotalsView avec filtres de date")
print("=" * 80)
request = factory.get('/stats/po/totals/?group_by=summary&start_date=2026-01-01&end_date=2026-03-31')
view = POTotalsView.as_view()
response = view(request)
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
print()

print("=" * 80)
print("TEST 3: POTotalsView avec filtre 'All' (devrait être ignoré)")
print("=" * 80)
request = factory.get('/stats/po/totals/?group_by=summary&department=All&supplier=All')
view = POTotalsView.as_view()
response = view(request)
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
print()

print("=" * 80)
print("TEST 4: total_price_dinar_view (total des PO approuvées)")
print("=" * 80)
request = factory.get('/stats/po/total-price-dinar/')
response = total_price_dinar_view(request)
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
print()

print("=" * 80)
print("TEST 5: total_price_dinar_view avec filtres")
print("=" * 80)
request = factory.get('/stats/po/total-price-dinar/?start_date=2026-01-01&end_date=2026-03-31')
response = total_price_dinar_view(request)
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
print()

print("=" * 80)
print("TEST 6: PORejectionRateView")
print("=" * 80)
request = factory.get('/stats/po/rejection-rate/?group_by=department')
view = PORejectionRateView.as_view()
response = view(request)
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
print()

print("=" * 80)
print("Vérification des PO en base de données")
print("=" * 80)
all_po = PurchaseOrder.objects.all()
print(f"Total PO: {all_po.count()}")
print(f"PO approuvées: {all_po.filter(statuss__iexact='approved').count()}")
print(f"PO rejetées: {all_po.filter(statuss__iexact='rejected').count()}")
print()
# datatable tests
print("=" * 80)
print("TEST 7: POListView datatable basique page 1")
print("=" * 80)
from datatable.views import POListView
request = factory.get('/datatable/po/list/?page=1&page_size=5')
view = POListView.as_view()
response = view(request)
print(f"Status: {response.status_code}")
print(f"Data keys: {list(response.data.keys())}")
print(f"Total count: {response.data.get('total')}")
print(f"Results length: {len(response.data.get('results', []))}")
print()

print("=" * 80)
print("TEST 8: POListView avec filtres (requester=userHR)")
print("=" * 80)
request = factory.get('/datatable/po/list/?page=1&page_size=5&requester=userHR')
view = POListView.as_view()
response = view(request)
print(f"Status: {response.status_code}")
print(f"Response data: {response.data}")
print()
