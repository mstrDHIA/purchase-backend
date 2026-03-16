#!/usr/bin/env python
"""
Script de test complet pour de faire fonctionner le calcul du total prix dinar
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purchase_backend.settings')
django.setup()

from department.models import Department
from custom_user.models import User
from purchase_order.models import PurchaseOrder

print("=" * 80)
print("🔧 ÉTAPE 1: Création des données de département et utilisateur")
print("=" * 80)

# Créer ou récupérer des départements
dept_it, created = Department.objects.get_or_create(id=1, defaults={'name': 'IT'})
dept_marketing, created = Department.objects.get_or_create(id=2, defaults={'name': 'Marketing'})

print(f"✅ Département IT: ID={dept_it.id}, Nom='{dept_it.name}'")
print(f"✅ Département Marketing: ID={dept_marketing.id}, Nom='{dept_marketing.name}'")

# Créer un utilisateur avec département
user, created = User.objects.get_or_create(
    id=1, 
    defaults={
        'username': 'userHR',
        'dep_id': dept_it,
        'first_name': 'User',
        'last_name': 'HR'
    }
)

print(f"✅ Utilisateur: username='{user.username}', Département={user.dep_id.name if user.dep_id else 'None'}")

print("\n" + "=" * 80)
print("🔧 ÉTAPE 2: Mise à jour des PurchaseOrders avec données réalistes")
print("=" * 80)

# Produits exemples
products_examples = [
    {'name': 'Impression', 'quantity': 12, 'unit_price': 3, 'currency': 'TND'},
    {'name': 'teste 3.2', 'quantity': 12, 'unit_price': 45, 'currency': 'EUR'},
    {'name': 'Electrique', 'quantity': 12, 'unit_price': 23, 'currency': 'DT'},
    {'name': 'Informatique', 'quantity': 44, 'unit_price': 34, 'currency': 'USD'},
    {'name': 'teste 2.2', 'quantity': 12, 'unit_price': 23, 'currency': 'TND'},
]

updated = 0
for i, po in enumerate(PurchaseOrder.objects.all()):
    product = products_examples[i % len(products_examples)]
    
    # Assigner les données
    po.products = {
        'name': product['name'],
        'quantity': product['quantity'],
        'unit_price': product['unit_price']
    }
    po.department = dept_it if i % 2 == 0 else dept_marketing
    po.requested_by_user = user
    po.currency = product['currency']
    po.statuss = 'approved' if i % 3 != 0 else 'rejected'
    po.save()
    
    price_local = product['quantity'] * product['unit_price']
    rates = {'TND': 1, 'USD': 3.1, 'EUR': 3.4, 'DT': 1}
    price_dinar = price_local * rates.get(product['currency'], 1)
    
    updated += 1
    status_label = "✅ APPROVED" if po.statuss == 'approved' else "❌ REJECTED"
    dept_label = "IT" if po.department.id == dept_it.id else "Marketing"
    print(f"PO {po.id}: {product['name']} x{product['quantity']} @ {product['unit_price']} {product['currency']} ({price_local} {product['currency']} = {price_dinar:.2f} DT) | {dept_label:9} | {status_label}")

print(f"\n✅ {updated} PO mises à jour avec données réalistes!\n")

print("=" * 80)
print("🧪 ÉTAPE 3: Test de l'endpoint /stats/po/total-price-dinar/")
print("=" * 80)

# Importer la fonction pour tester
from django.test import RequestFactory
from statistic.views import total_price_dinar_view
from django.http import QueryDict

factory = RequestFactory()

# Test 1: Sans filtre
print("\n📝 Test 1: GET /stats/po/total-price-dinar/")
request = factory.get('/stats/po/total-price-dinar/')
response = total_price_dinar_view(request)
print(f"Response: {response.data}")

# Test 2: Avec filtre département IT
print("\n📝 Test 2: GET /stats/po/total-price-dinar/?department=1 (IT)")
request = factory.get('/stats/po/total-price-dinar/?department=1')
response = total_price_dinar_view(request)
print(f"Response: {response.data}")

# Test 3: Avec filtre département Marketing
print("\n📝 Test 3: GET /stats/po/total-price-dinar/?department=2 (Marketing)")
request = factory.get('/stats/po/total-price-dinar/?department=2')
response = total_price_dinar_view(request)
print(f"Response: {response.data}")

print("\n" + "=" * 80)
print("✅ Tests terminés!")
print("=" * 80)
