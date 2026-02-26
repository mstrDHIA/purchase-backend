from rest_framework.decorators import api_view


@api_view(['GET'])
def total_price_dinar_view(request):
    totals = get_total_price_by_currency(request)
    return Response(totals)


def get_total_price_by_currency(request):
    """
    Calcule la somme du total price des PurchaseOrders filtrés, séparée par devise (TND, USD, EUR),
    et donne aussi le total converti en dinar.
    """
    # On filtre uniquement les PO approuvées
    def only_approved(po):
        return (getattr(po, 'statuss', '').lower() == 'approved')

    qs = get_filtered_purchase_orders(request, include_status_filter=True)
    if isinstance(qs, list):
        qs = [po for po in qs if only_approved(po)]
    else:
        qs = qs.filter(statuss__iexact='approved')
    rates = {'TND': 1, 'USD': 3.1, 'EUR': 3.4}
    totals = {'TND': 0, 'USD': 0, 'EUR': 0}

    def normalize_currency(cur):
        if not cur:
            return 'TND'
        c = str(cur).strip().upper()
        c_no_space = c.replace(' ', '').replace('.', '')
        # Symbol detection (robuste)
        if '€' in c or '€' in c_no_space:
            return 'EUR'
        if '$' in c or '$' in c_no_space:
            return 'USD'
        if 'DT' in c or 'TND' in c or 'DT' in c_no_space or 'TND' in c_no_space:
            return 'TND'
        # Text detection
        if c in ['EUR', 'EURO']:
            return 'EUR'
        if c in ['USD', 'US DOLLAR', 'DOLLAR']:
            return 'USD'
        if c in ['TND', 'DT', 'DINAR']:
            return 'TND'
        return c

    def calc_total_price(po):
        products = getattr(po, 'products', [])
        if isinstance(products, dict):
            products = [products]
        total = 0
        for item in products:
            try:
                qty = float(item.get('quantity', 0))
                unit = float(item.get('unit_price', 0))
                total += qty * unit
            except Exception as e:
                print(f"[DEBUG] Erreur calcul produit: {item} => {e}")
        return total

    if isinstance(qs, list):
        for po in qs:
            currency_raw = getattr(po, 'currency', None)
            currency = normalize_currency(currency_raw)
            # Si currency n'est pas reconnu, essayer de détecter dans le champ unit_price
            if currency not in totals:
                products = getattr(po, 'products', [])
                if isinstance(products, dict):
                    products = [products]
                for item in products:
                    unit_raw = str(item.get('unit_price', ''))
                    unit_raw_no_space = unit_raw.replace(' ', '')
                    if '€' in unit_raw or '€' in unit_raw_no_space:
                        currency = 'EUR'
                        break
                    if '$' in unit_raw or '$' in unit_raw_no_space:
                        currency = 'USD'
                        break
                    if 'DT' in unit_raw or 'TND' in unit_raw or 'DT' in unit_raw_no_space or 'TND' in unit_raw_no_space:
                        currency = 'TND'
                        break
            print(f"[DEBUG] PO {getattr(po, 'id', None)}: devise détectée = {currency}")
            if currency not in totals:
                continue
            part = calc_total_price(po)
            totals[currency] += part
    else:
        for po in qs:
            currency_raw = getattr(po, 'currency', None)
            currency = normalize_currency(currency_raw)
            if currency not in totals:
                products = getattr(po, 'products', [])
                if isinstance(products, dict):
                    products = [products]
                for item in products:
                    unit_raw = str(item.get('unit_price', ''))
                    unit_raw_no_space = unit_raw.replace(' ', '')
                    if '€' in unit_raw or '€' in unit_raw_no_space:
                        currency = 'EUR'
                        break
                    if '$' in unit_raw or '$' in unit_raw_no_space:
                        currency = 'USD'
                        break
                    if 'DT' in unit_raw or 'TND' in unit_raw or 'DT' in unit_raw_no_space or 'TND' in unit_raw_no_space:
                        currency = 'TND'
                        break
            print(f"[DEBUG] PO {getattr(po, 'id', None)}: devise détectée = {currency}")
            if currency not in totals:
                continue
            part = calc_total_price(po)
            totals[currency] += part

    return {
        'total_price_tnd': totals['TND'],
        'total_price_usd': totals['USD'],
        'total_price_eur': totals['EUR']
    }

from django.db.models import Count, Q, F
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

from purchase_order.models import PurchaseOrder
from purchase_order.serializers import PurchaseOrderSerializer


def parse_date_params(request):
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    return start, end


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

    # product-related filters require inspecting the JSON stored in `products`
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
            start, end = parse_date_params(request)
            dept_filter = request.GET.get('department')
            requester_filter = request.GET.get('requester')

            qs = PurchaseOrder.objects.all()
            if start:
                qs = qs.filter(created_at__date__gte=start)
            if end:
                qs = qs.filter(created_at__date__lte=end)

            if dept_filter:
                # filter by PO.department OR requester's department
                if dept_filter.isdigit():
                    qs = qs.filter(
                        Q(purchase_request__requested_by__dep_id__id=int(dept_filter)) | Q(requested_by_user__dep_id__id=int(dept_filter)) | Q(department__id=int(dept_filter))
                    )
                else:
                    qs = qs.filter(
                        Q(purchase_request__requested_by__dep_id__name__iexact=dept_filter) | Q(requested_by_user__dep_id__name__iexact=dept_filter) | Q(department__name__iexact=dept_filter)
                    )
            if requester_filter:
                # prefer filtering by PR creator (purchase_request.requested_by), fallback to PO.requested_by_user
                if requester_filter.isdigit():
                    qs = qs.filter(
                        Q(purchase_request__requested_by__id=int(requester_filter)) | Q(requested_by_user__id=int(requester_filter))
                    )
                else:
                    qs = qs.filter(
                        Q(purchase_request__requested_by__username__iexact=requester_filter) | Q(requested_by_user__username__iexact=requester_filter)
                    )

            # consider rejected if rejected_reason set OR statuss == 'rejected'
            rejected_q = Q(rejected_reason__isnull=False) | Q(statuss__iexact='rejected')

            if group_by == 'department':
                data = qs.values('purchase_request__requested_by__dep_id__id', 'purchase_request__requested_by__dep_id__name').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'department_id': d['purchase_request__requested_by__dep_id__id'], 'department': d['purchase_request__requested_by__dep_id__name'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific department filter is provided, return single summary
                if dept_filter and result:
                    return Response(result[0])
                return Response(result)

            if group_by == 'requester':
                data = qs.values('purchase_request__requested_by__id', 'purchase_request__requested_by__username').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'requester_id': d['purchase_request__requested_by__id'], 'requester': d['purchase_request__requested_by__username'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific requester filter is provided, return single summary
                if requester_filter and result:
                    return Response(result[0])
                return Response(result)

            return Response({'detail': 'Invalid group_by parameter'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
