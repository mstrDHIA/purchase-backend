from rest_framework.decorators import api_view

@api_view(['GET'])
def total_price_dinar_view(request):
    """
    Retourne les totaux des prix des PurchaseOrders approuvées par devise.
    Calcule le total pour chaque devise séparément, puis convertit tout en dinar.
    """
    # Get filtered orders excluding reject/approval status filter base (we'll apply our own below)
    qs = get_filtered_purchase_orders(request, include_status_filter=False)

    # Filter to only approved orders (statuss='approved' and no rejected_reason)
    if isinstance(qs, list):
        qs = [po for po in qs if (getattr(po, 'statuss', '').lower() == 'approved' and po.rejected_reason_id is None)]
    else:
        qs = qs.filter(statuss__iexact='approved').exclude(rejected_reason__isnull=False)

    # Apply department filter if provided
    dept_filter = request.GET.get('department')
    if dept_filter:
        if isinstance(qs, list):
            if dept_filter.isdigit():
                qs = [po for po in qs if po.department and po.department.id == int(dept_filter)]
            else:
                qs = [po for po in qs if po.department and po.department.name.lower() == dept_filter.lower()]
        else:
            if dept_filter.isdigit():
                qs = qs.filter(department__id=int(dept_filter))
            else:
                qs = qs.filter(department__name__iexact=dept_filter)

    rates = {'TND': 1, 'USD': 3.1, 'EUR': 3.4, 'DT': 1}

    def calc_total_price(po):
        """Calculate total price from products JSON field with flexible key matching"""
        products = getattr(po, 'products', [])
        if isinstance(products, dict):
            products = [products]
        elif isinstance(products, str):
            try:
                products = json.loads(products)
                if isinstance(products, dict):
                    products = [products]
            except:
                products = []

        if not products:
            return 0

        total = 0
        for item in products:
            # Handle if item is a string
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except:
                    continue

            if not isinstance(item, dict):
                continue

            try:
                # Try different key names for quantity
                qty = 0
                for qty_key in ('quantity', 'qty', 'quantite', 'amount'):
                    if qty_key in item and item[qty_key]:
                        qty = float(item[qty_key])
                        break

                # Try different key names for unit price
                unit = 0
                for unit_key in ('unit_price', 'unitPrice', 'price', 'unit_cost', 'unitCost', 'prix'):
                    if unit_key in item and item[unit_key]:
                        unit = float(item[unit_key])
                        break

                # If we found both, add to total
                if qty > 0 and unit > 0:
                    total += qty * unit
                # Otherwise try direct total_price field
                elif 'total_price' in item or 'totalPrice' in item or 'total' in item:
                    total_key = None
                    for key in ('total_price', 'totalPrice', 'total'):
                        if key in item:
                            total_key = key
                            break
                    if total_key:
                        total += float(item[total_key])
            except Exception as e:
                print(f"[DEBUG] Erreur calcul produit: {item} => {e}")
                continue

        return total

    # Calculate totals by currency
    totals_by_currency = {'TND': 0.0, 'USD': 0.0, 'EUR': 0.0}
    total_in_dinar = 0.0

    if isinstance(qs, list):
        for po in qs:
            curr = getattr(po, 'currency', 'TND') or 'TND'
            # Normalize currency codes
            if curr.upper() == 'DT':
                curr = 'TND'

            price = calc_total_price(po)
            if curr in totals_by_currency:
                totals_by_currency[curr] += price
            else:
                totals_by_currency[curr] = price

            # Convert to dinar for total
            rate = rates.get(curr.upper(), 1)
            total_in_dinar += price * rate
    else:
        for po in qs:
            curr = getattr(po, 'currency', 'TND') or 'TND'
            # Normalize currency codes
            if curr.upper() == 'DT':
                curr = 'TND'

            price = calc_total_price(po)
            if curr in totals_by_currency:
                totals_by_currency[curr] += price
            else:
                totals_by_currency[curr] = price

            # Convert to dinar for total
            rate = rates.get(curr.upper(), 1)
            total_in_dinar += price * rate

    return Response({
        'total_price_tnd': totals_by_currency['TND'],
        'total_price_usd': totals_by_currency['USD'],
        'total_price_eur': totals_by_currency['EUR'],
        'total_price_dinar': total_in_dinar,  # Total converti en dinar
    })

def get_total_price_dinar(request):
    """
    Calcule la somme du total price des PurchaseOrders approuvés (pas rejetés) et filtrés, 
    convertis en dinar selon la devise.
    Taux fixes : 1 USD = 3.1 TND, 1 EUR = 3.4 TND, 1 TND = 1 TND.
    Supports department filter via ?department=<id_or_name>
    """
    # Get filtered orders excluding reject/approval status filter base (we'll apply our own below)
    qs = get_filtered_purchase_orders(request, include_status_filter=False)
    
    # Filter to only approved orders (statuss='approved' and no rejected_reason)
    if isinstance(qs, list):
        qs = [po for po in qs if (getattr(po, 'statuss', '').lower() == 'approved' and po.rejected_reason_id is None)]
    else:
        qs = qs.filter(statuss__iexact='approved').exclude(rejected_reason__isnull=False)
    
    # Apply department filter if provided
    dept_filter = request.GET.get('department')
    if dept_filter:
        if isinstance(qs, list):
            if dept_filter.isdigit():
                qs = [po for po in qs if po.department and po.department.id == int(dept_filter)]
            else:
                qs = [po for po in qs if po.department and po.department.name.lower() == dept_filter.lower()]
        else:
            if dept_filter.isdigit():
                qs = qs.filter(department__id=int(dept_filter))
            else:
                qs = qs.filter(department__name__iexact=dept_filter)
    
    # Affiche les IDs des PO filtrés et le filtre utilisé
    if isinstance(qs, list):
        print(f"[DEBUG] Department filter: {dept_filter}, Approved PO IDs: {[getattr(po, 'id', None) for po in qs]}")
        for po in qs:
            dep = getattr(po, 'department', None)
            dep_id = getattr(dep, 'id', None) if dep else None
            dep_name = getattr(dep, 'name', None) if dep else None
            try:
                pr_dep = po.purchase_request.requested_by.dep_id if po.purchase_request and po.purchase_request.requested_by else None
            except Exception:
                pr_dep = None
            try:
                user_dep = po.requested_by_user.dep_id if po.requested_by_user else None
            except Exception:
                user_dep = None
            print(f"[DEBUG] PO {po.id}: department=({dep_id}, {dep_name}), products={po.products}, PR_dep={pr_dep}, user_dep={user_dep}")
    else:
        print(f"[DEBUG] Department filter: {dept_filter}, Approved PO IDs: {[po.id for po in qs]}")
        for po in qs:
            # Try to get department info from PO, PR creator, and requester for debugging
            dep = getattr(po, 'department', None)
            dep_id = getattr(dep, 'id', None) if dep else None
            dep_name = getattr(dep, 'name', None) if dep else None
            try:
                pr_dep = po.purchase_request.requested_by.dep_id if po.purchase_request and po.purchase_request.requested_by else None
            except Exception:
                pr_dep = None
            try:
                user_dep = po.requested_by_user.dep_id if po.requested_by_user else None
            except Exception:
                user_dep = None
            print(f"[DEBUG] PO {po.id}: department=({dep_id}, {dep_name}), products={po.products}, PR_dep={pr_dep}, user_dep={user_dep}")
    rates = {'TND': 1, 'USD': 3.1, 'EUR': 3.4}
    def calc_total_price(po):
        """Calculate total price from products JSON field with flexible key matching"""
        products = getattr(po, 'products', [])
        if isinstance(products, dict):
            products = [products]
        elif isinstance(products, str):
            try:
                products = json.loads(products)
                if isinstance(products, dict):
                    products = [products]
            except:
                products = []
        
        if not products:
            return 0
            
        total = 0
        for item in products:
            # Handle if item is a string
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except:
                    continue
            
            if not isinstance(item, dict):
                continue
            
            try:
                # Try different key names for quantity
                qty = 0
                for qty_key in ('quantity', 'qty', 'quantite', 'amount'):
                    if qty_key in item and item[qty_key]:
                        qty = float(item[qty_key])
                        break
                
                # Try different key names for unit price
                unit = 0
                for unit_key in ('unit_price', 'unitPrice', 'price', 'unit_cost', 'unitCost', 'prix'):
                    if unit_key in item and item[unit_key]:
                        unit = float(item[unit_key])
                        break
                
                # If we found both, add to total
                if qty > 0 and unit > 0:
                    item_total = qty * unit
                    total += item_total
                    print(f"[DEBUG] Produit trouvé: qty={qty}, unit={unit}, subtotal={item_total}")
                # Otherwise try direct total_price field
                elif 'total_price' in item or 'totalPrice' in item or 'total' in item:
                    total_key = None
                    for key in ('total_price', 'totalPrice', 'total'):
                        if key in item:
                            total_key = key
                            break
                    if total_key:
                        item_total = float(item[total_key])
                        total += item_total
                        print(f"[DEBUG] Produit trouvé via {total_key}={item_total}")
                else:
                    print(f"[DEBUG] ⚠️ Produit sans prix: {item.keys()}")
            except Exception as e:
                print(f"[DEBUG] Erreur calcul produit: {item} => {e}")
                continue
        
        return total

    def to_tnd(amount, currency):
        rate = rates.get((currency or 'TND').upper(), 1)
        return amount * rate

    if isinstance(qs, list):
        total = 0
        for po in qs:
            part = to_tnd(calc_total_price(po), getattr(po, 'currency', 'TND'))
            print(f"[DEBUG] PO {getattr(po, 'id', None)}: total_price_dinar_partiel={part}")
            total += part
        print(f"[DEBUG] Nombre de PO filtrés: {len(qs)}")
    else:
        total = 0
        count = 0
        for po in qs:
            part = to_tnd(calc_total_price(po), getattr(po, 'currency', 'TND'))
            print(f"[DEBUG] PO {getattr(po, 'id', None)}: total_price_dinar_partiel={part}")
            total += part
            count += 1
        print(f"[DEBUG] Nombre de PO filtrés: {count}")
    print(f"[DEBUG] Somme totale en dinar: {total}")
    return total

from django.db.models import Count, Q, F
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

from purchase_order.models import PurchaseOrder
from purchase_order.serializers import PurchaseOrderSerializer


def parse_date_params(request):
    # Support multiple date parameter names for flexibility
    start = request.GET.get('start_date') or request.GET.get('from_date') or request.GET.get('fromDate') or request.GET.get('FromDate')
    end = request.GET.get('end_date') or request.GET.get('to_date') or request.GET.get('toDate') or request.GET.get('ToDate')
    # Treat empty strings as None
    return (start or None), (end or None)


def _prod_field_str(item, *field_names):
    """Safely extract a string value for product fields.

    If the field value is a dict, try common name keys ('name','title','label').
    Return empty string when no usable string is found.
    """
    # If item is a JSON string, try to parse it
    if isinstance(item, str):
        try:
            parsed = json.loads(item)
            if isinstance(parsed, dict):
                item = parsed
            else:
                return ''
        except Exception:
            return ''
    if not isinstance(item, dict):
        return ''
    for fname in field_names:
        v = item.get(fname)
        if v is None:
            continue
        if isinstance(v, dict):
            name = v.get('name') or v.get('title') or v.get('label')
            if name:
                return str(name)
            continue
        return str(v)
    return ''


def _prod_supplier_id(item):
    """Return supplier id if present, otherwise None."""
    if isinstance(item, str):
        try:
            item = json.loads(item)
        except Exception:
            return None
    if not isinstance(item, dict):
        return None
    # common places for supplier id
    supplier = item.get('supplier')
    if isinstance(supplier, dict):
        return supplier.get('id') or supplier.get('pk')
    # sometimes supplier stored as id directly
    if isinstance(supplier, int):
        return supplier
    # fallback keys
    for k in ('supplier_id', 'supplierId', 'supplierID'):
        v = item.get(k)
        if isinstance(v, int):
            return v
        try:
            if isinstance(v, str) and v.isdigit():
                return int(v)
        except Exception:
            pass
    return None


def get_filtered_purchase_orders(request, include_status_filter=True):
    """Return a QuerySet or a list of PurchaseOrder objects filtered according to
    the same rules used by POTotalsView. If product-related filters are present
    a list is returned because products are stored as JSON and require
    in-memory inspection.
    """
    start, end = parse_date_params(request)
    dept_filter = request.GET.get('department')
    requester_filter = request.GET.get('requester')
    exclude_null_dept = str(request.GET.get('exclude_null_dept', 'false')).lower() in ('1', 'true', 'yes')
    category_filter = request.GET.get('category')
    subcategory_filter = request.GET.get('subcategory')
    supplier_filter = request.GET.get('supplier')
    family_filter = request.GET.get('family')
    subfamily_filter = request.GET.get('subfamily')
    
    # Treat 'All' as None (no filter)
    def _normalize_filter(value):
        if value and value.lower() not in ('all', 'none', ''):
            return value
        return None
    
    dept_filter = _normalize_filter(dept_filter)
    requester_filter = _normalize_filter(requester_filter)
    category_filter = _normalize_filter(category_filter)
    subcategory_filter = _normalize_filter(subcategory_filter)
    supplier_filter = _normalize_filter(supplier_filter)
    family_filter = _normalize_filter(family_filter)
    subfamily_filter = _normalize_filter(subfamily_filter)

    qs = PurchaseOrder.objects.all()
    if include_status_filter:
        qs = qs.filter(Q(statuss__iexact='approved') | Q(statuss__iexact='rejected'))
    if start:
        qs = qs.filter(created_at__date__gte=start)
    if end:
        qs = qs.filter(created_at__date__lte=end)

    if exclude_null_dept:
        qs = qs.exclude(requested_by_user__dep_id__isnull=True)

    if dept_filter:
        if dept_filter.isdigit():
            qs = qs.filter(
                Q(purchase_request__requested_by__dep_id__id=int(dept_filter)) | Q(requested_by_user__dep_id__id=int(dept_filter)) | Q(department__id=int(dept_filter))
            )
        else:
            qs = qs.filter(
                Q(purchase_request__requested_by__dep_id__name__iexact=dept_filter) | Q(requested_by_user__dep_id__name__iexact=dept_filter) | Q(department__name__iexact=dept_filter)
            )
    if requester_filter:
        if requester_filter.isdigit():
            qs = qs.filter(
                Q(purchase_request__requested_by__id=int(requester_filter)) | Q(requested_by_user__id=int(requester_filter))
            )
        else:
            qs = qs.filter(
                Q(purchase_request__requested_by__username__iexact=requester_filter) | Q(requested_by_user__username__iexact=requester_filter)
            )

    # product-related filters require inspecting the JSON stored ivn `products`
    if any([category_filter, subcategory_filter, supplier_filter, family_filter, subfamily_filter]):
        qs_list = list(qs)

        if category_filter:
            qs_list = [po for po in qs_list if any(
                _prod_field_str(item, 'category', 'category_name').lower() == str(category_filter).lower()
                for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
            )]

        if subcategory_filter:
            qs_list = [po for po in qs_list if any(
                _prod_field_str(item, 'subcategory', 'subcategory_name').lower() == str(subcategory_filter).lower()
                for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
            )]

        if supplier_filter:
            supplier_is_digit = supplier_filter.isdigit()
            supplier_int = int(supplier_filter) if supplier_is_digit else None
            qs_list = [po for po in qs_list if any(
                (
                    (_prod_field_str(item, 'supplier', 'supplier_name').lower() == str(supplier_filter).lower())
                    if _prod_field_str(item, 'supplier', 'supplier_name') else False
                ) or (
                    supplier_is_digit and (_prod_supplier_id(item) == supplier_int)
                )
                for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
            )]

        if family_filter:
            qs_list = [po for po in qs_list if any(
                _prod_field_str(item, 'family', 'family_name').lower() == str(family_filter).lower()
                for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
            )]

        if subfamily_filter:
            qs_list = [po for po in qs_list if any(
                _prod_field_str(item, 'subfamily', 'subfamily_name').lower() == str(subfamily_filter).lower()
                for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
            )]

        return qs_list

    return qs


class POTotalsView(APIView):
    """Return totals of PurchaseOrders in a given period grouped by department, requester, category, subcategory or supplier."""

    def get(self, request):
        try:
            group_by = request.GET.get('group_by', 'summary')
            # Use shared helper to build filtered queryset/list
            qs = get_filtered_purchase_orders(request, include_status_filter=True)
            # expose some filter flags used later
            dept_filter = request.GET.get('department')
            requester_filter = request.GET.get('requester')
            category_filter = request.GET.get('category')
            subcategory_filter = request.GET.get('subcategory')
            supplier_filter = request.GET.get('supplier')
            family_filter = request.GET.get('family')
            subfamily_filter = request.GET.get('subfamily')
            has_any_filter = any([dept_filter, requester_filter, category_filter, subcategory_filter, supplier_filter, family_filter, subfamily_filter])

            # consider a PO rejected if it has a rejected_reason OR its statuss (typo field) is 'rejected'
            rejected_q = Q(rejected_reason__isnull=False) | Q(statuss__iexact='rejected')
            
            # Check if ANY specific filter is provided (for single summary response)
            has_any_filter = any([dept_filter, requester_filter, category_filter, subcategory_filter, supplier_filter, family_filter, subfamily_filter])

            # Default summary view: return global totals
            if group_by == 'summary':
                if isinstance(qs, list):
                    total = len(qs)
                    rejected = sum(1 for po in qs if any([
                        po.rejected_reason is not None,
                        (po.statuss or '').lower() == 'rejected'
                    ]))
                else:
                    total = qs.count()
                    rejected = qs.filter(rejected_q).count()
                
                rejection_rate = (rejected / total) if total else 0
                return Response({
                    'total': total,
                    'rejected': rejected,
                    'rejection_rate': rejection_rate,
                })

            if group_by == 'department':
                # group by department preferring PR creator's department, then requester's department, then PO.department
                qs_annot = qs.annotate(
                    dept_id=Coalesce(F('purchase_request__requested_by__dep_id__id'), F('requested_by_user__dep_id__id'), F('department__id')),
                    dept_name=Coalesce(F('purchase_request__requested_by__dep_id__name'), F('requested_by_user__dep_id__name'), F('department__name')),
                )
                data = qs_annot.values('dept_id', 'dept_name').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'department_id': d['dept_id'], 'department': d['dept_name'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific department filter is provided, return single summary
                if dept_filter and result:
                    return Response(result[0])
                return Response(result)

            if group_by == 'requester':
                # group by the PR creator (preferred)
                data = qs.values('purchase_request__requested_by__id', 'purchase_request__requested_by__username').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'requester_id': d['purchase_request__requested_by__id'], 'requester': d['purchase_request__requested_by__username'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific requester filter is provided, return single summary
                if requester_filter and result:
                    return Response(result[0])
                return Response(result)

            if group_by in ('category', 'subcategory', 'supplier', 'family', 'subfamily'):
                # At this point, qs is already filtered by product attributes above
                # Now just group by the requested attribute
                # Make sure qs is a list for iteration
                if not isinstance(qs, list):
                    qs = list(qs)
                
                counts_total = {}
                counts_rejected = {}
                # iterate per PO and count each key once per PO
                for po in qs:
                    products = po.products or []
                    if isinstance(products, dict):
                        products = [products]
                    keys_in_po = set()
                    for item in products:
                        key = None
                        if group_by == 'category':
                            key = _prod_field_str(item, 'category', 'category_name')
                        elif group_by == 'subcategory':
                            key = _prod_field_str(item, 'subcategory', 'subcategory_name')
                        elif group_by == 'family':
                            key = _prod_field_str(item, 'family', 'family_name')
                        elif group_by == 'subfamily':
                            key = _prod_field_str(item, 'subfamily', 'subfamily_name')
                        else:
                            key = _prod_field_str(item, 'supplier', 'supplier_name')
                        if key:
                            keys_in_po.add(key)
                    for key in keys_in_po:
                        counts_total[key] = counts_total.get(key, 0) + 1
                        # treat rejected if rejected_reason set OR statuss == 'rejected'
                        if (po.rejected_reason_id is not None) or (getattr(po, 'statuss', '').lower() == 'rejected'):
                            counts_rejected[key] = counts_rejected.get(key, 0) + 1

                # If any specific filter is provided, return single summary
                if has_any_filter:
                    # Sum all totals and rejected across all remaining keys
                    total_sum = sum(counts_total.values())
                    rejected_sum = sum(counts_rejected.values())
                    filter_name = category_filter or subcategory_filter or supplier_filter or family_filter or subfamily_filter or f"Filtered {group_by}"
                    return Response({'name': filter_name, 'total': total_sum, 'rejected': rejected_sum, 'rejection_rate': (rejected_sum / total_sum) if total_sum else 0})

                result = [{'name': k, 'total': counts_total.get(k, 0), 'rejected': counts_rejected.get(k, 0), 'rejection_rate': (counts_rejected.get(k, 0) / counts_total.get(k, 0)) if counts_total.get(k, 0) else 0} for k in sorted(counts_total.keys(), key=lambda x: -counts_total.get(x, 0))]
                return Response(result)

            return Response({'detail': 'Invalid group_by parameter'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PORejectionRateView(APIView):
    """Return rejection rates grouped by department or requester."""

    def get(self, request):
        try:
            group_by = request.GET.get('group_by', 'department')
            # Use the same filtering logic as POTotalsView for consistency
            qs = get_filtered_purchase_orders(request, include_status_filter=False)
            
            # consider rejected if rejected_reason set OR statuss == 'rejected'
            rejected_q = Q(rejected_reason__isnull=False) | Q(statuss__iexact='rejected')
            
            # Make sure qs is a QuerySet for aggregation
            if isinstance(qs, list):
                qs = PurchaseOrder.objects.filter(id__in=[po.id for po in qs])

            if group_by == 'department':
                # Use the same Coalesce approach as POTotalsView
                qs_annot = qs.annotate(
                    dept_id=Coalesce(F('purchase_request__requested_by__dep_id__id'), F('requested_by_user__dep_id__id'), F('department__id')),
                    dept_name=Coalesce(F('purchase_request__requested_by__dep_id__name'), F('requested_by_user__dep_id__name'), F('department__name')),
                )
                data = qs_annot.values('dept_id', 'dept_name').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'department_id': d['dept_id'], 'department': d['dept_name'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                return Response(result)

            if group_by == 'requester':
                # Use the same approach as POTotalsView (prefer PR creator)
                data = qs.values('purchase_request__requested_by__id', 'purchase_request__requested_by__username').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'requester_id': d['purchase_request__requested_by__id'], 'requester': d['purchase_request__requested_by__username'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                return Response(result)

            return Response({'detail': 'Invalid group_by parameter'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
