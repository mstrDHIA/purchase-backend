import os
import django
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'purchase_backend.settings')
django.setup()

from department.models import Department
from custom_user.models import User
from purchase_order.models import PurchaseOrder

# Utiliser la date du jour
today = datetime.now()

# Récupérer ou créer les départements
dept_it, _ = Department.objects.get_or_create(id=1, defaults={'name': 'IT'})
dept_marketing, _ = Department.objects.get_or_create(id=2, defaults={'name': 'Marketing'})

# Récupérer ou créer l'utilisateur
user, _ = User.objects.get_or_create(id=1, defaults={'username': 'userHR', 'dep_id': dept_it})

print(f"✅ Date du jour: {today.date()}")
print(f"✅ Département: {dept_it.name}, {dept_marketing.name}")

# Mettre à jour TOUS les POs existants
pos = PurchaseOrder.objects.all()
updated = 0

for i, po in enumerate(pos):
    # Mettre à jour la date de création
    po.created_at = today - timedelta(days=5-i%5)  # Entre 5 jours avant et maintenant
    
    # Department assignment
    po.department = dept_it if i % 2 == 0 else dept_marketing
    po.requested_by_user = user
    
    # Garder les produits existants s'ils ont la bonne structure
    products = po.products or {'quantity': 0, 'unit_price': 0}
    
    # Asurer que le statut est correct
    if i % 3 == 0:
        po.statuss = 'rejected'
    else:
        po.statuss = 'approved'
    
    # Currency normalisée: EUR, USD, TND
    if po.currency and po.currency.upper() in ['EUR', 'USD', 'TND']:
        pass  # OK
    elif po.currency and po.currency.upper() == 'DT':
        po.currency = 'TND'  # DT = TND
    else:
        po.currency = 'TND'  # Default
    
    po.save()
    updated += 1
    
    qty = products.get('quantity', 0)
    unit_price = products.get('unit_price', 0)
    total_local = qty * unit_price

    print(f"PO {po.id}: {po.products.get('name', 'Unknown')}, Status={po.statuss:8}, Dept={po.department.name:9}, Created={po.created_at.date()}, Currency={po.currency}")

print(f"\n✅ {updated} POs updated successfully!")
print(f"\n🔗 Test the endpoint:")
print(f"   http://localhost:8000/stats/po/total-price-dinar/")
