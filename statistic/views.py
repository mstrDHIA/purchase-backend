from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from purchase_order.models import PurchaseOrder


def parse_date_params(request):
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    return start, end


class POTotalsView(APIView):
    """Return totals of PurchaseOrders in a given period grouped by department, requester, category, subcategory or supplier."""

    def get(self, request):
        try:
            group_by = request.GET.get('group_by', 'department')
            start, end = parse_date_params(request)
            dept_filter = request.GET.get('department')
            requester_filter = request.GET.get('requester')
            # default: include PO without department (exclude_null_dept=false)
            exclude_null_dept = request.GET.get('exclude_null_dept', 'false').lower() in ('1', 'true', 'yes')
            category_filter = request.GET.get('category')
            subcategory_filter = request.GET.get('subcategory')
            supplier_filter = request.GET.get('supplier')

            qs = PurchaseOrder.objects.all()
            if start:
                qs = qs.filter(created_at__date__gte=start)
            if end:
                qs = qs.filter(created_at__date__lte=end)

            if exclude_null_dept:
                qs = qs.exclude(requested_by_user__dep_id__isnull=True)

            if dept_filter:
                # allow filtering by either the requester's department or the PO's explicit department
                if dept_filter.isdigit():
                    qs = qs.filter(
                        Q(requested_by_user__dep_id__id=int(dept_filter)) | Q(department__id=int(dept_filter))
                    )
                else:
                    qs = qs.filter(
                        Q(requested_by_user__dep_id__name__iexact=dept_filter) | Q(department__name__iexact=dept_filter)
                    )
            if requester_filter:
                # allow filtering by PO.requested_by_user OR the original PR creator linked via purchase_request
                if requester_filter.isdigit():
                    qs = qs.filter(
                        Q(requested_by_user__id=int(requester_filter)) | Q(purchase_request__requested_by__id=int(requester_filter))
                    )
                else:
                    qs = qs.filter(
                        Q(requested_by_user__username__iexact=requester_filter) | Q(purchase_request__requested_by__username__iexact=requester_filter)
                    )

            rejected_q = Q(rejected_reason__isnull=False)
            
            # Check if ANY specific filter is provided (for single summary response)
            has_any_filter = any([dept_filter, requester_filter, category_filter, subcategory_filter, supplier_filter])

            if group_by == 'department':
                data = qs.values('requested_by_user__dep_id__id', 'requested_by_user__dep_id__name').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'department_id': d['requested_by_user__dep_id__id'], 'department': d['requested_by_user__dep_id__name'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific department filter is provided, return single summary
                if dept_filter and result:
                    return Response(result[0])
                return Response(result)

            if group_by == 'requester':
                data = qs.values('requested_by_user__id', 'requested_by_user__username').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'requester_id': d['requested_by_user__id'], 'requester': d['requested_by_user__username'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific requester filter is provided, return single summary
                if requester_filter and result:
                    return Response(result[0])
                return Response(result)

            if group_by in ('category', 'subcategory', 'supplier'):
                # Filter qs by category/subcategory/supplier if provided
                if category_filter:
                    qs = [po for po in qs if any(
                        (item.get('category') or item.get('category_name')) == category_filter 
                        for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
                    )]
                if subcategory_filter:
                    qs = [po for po in qs if any(
                        (item.get('subcategory') or item.get('subcategory_name')) == subcategory_filter 
                        for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
                    )]
                if supplier_filter:
                    qs = [po for po in qs if any(
                        (item.get('supplier') or item.get('supplier_name')) == supplier_filter 
                        for item in (po.products or [] if not isinstance(po.products, dict) else [po.products])
                    )]
                
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
                            key = item.get('category') or item.get('category_name')
                        elif group_by == 'subcategory':
                            key = item.get('subcategory') or item.get('subcategory_name')
                        else:
                            key = item.get('supplier') or item.get('supplier_name')
                        if key:
                            keys_in_po.add(key)
                    for key in keys_in_po:
                        counts_total[key] = counts_total.get(key, 0) + 1
                        if po.rejected_reason_id is not None:
                            counts_rejected[key] = counts_rejected.get(key, 0) + 1

                # If any specific filter is provided, return single summary
                if has_any_filter:
                    # Sum all totals and rejected across all remaining keys
                    total_sum = sum(counts_total.values())
                    rejected_sum = sum(counts_rejected.values())
                    filter_name = category_filter or subcategory_filter or supplier_filter or f"Filtered {group_by}"
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
                        Q(requested_by_user__dep_id__id=int(dept_filter)) | Q(department__id=int(dept_filter))
                    )
                else:
                    qs = qs.filter(
                        Q(requested_by_user__dep_id__name__iexact=dept_filter) | Q(department__name__iexact=dept_filter)
                    )
            if requester_filter:
                # filter by PO.requested_by_user OR the original PR creator linked via purchase_request
                if requester_filter.isdigit():
                    qs = qs.filter(
                        Q(requested_by_user__id=int(requester_filter)) | Q(purchase_request__requested_by__id=int(requester_filter))
                    )
                else:
                    qs = qs.filter(
                        Q(requested_by_user__username__iexact=requester_filter) | Q(purchase_request__requested_by__username__iexact=requester_filter)
                    )

            rejected_q = Q(rejected_reason__isnull=False)

            if group_by == 'department':
                data = qs.values('requested_by_user__dep_id__id', 'requested_by_user__dep_id__name').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'department_id': d['requested_by_user__dep_id__id'], 'department': d['requested_by_user__dep_id__name'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific department filter is provided, return single summary
                if dept_filter and result:
                    return Response(result[0])
                return Response(result)

            if group_by == 'requester':
                data = qs.values('requested_by_user__id', 'requested_by_user__username').annotate(total=Count('id'), rejected=Count('id', filter=rejected_q)).order_by('-total')
                result = [{'requester_id': d['requested_by_user__id'], 'requester': d['requested_by_user__username'], 'total': d['total'], 'rejected': d['rejected'], 'rejection_rate': (d['rejected'] / d['total']) if d['total'] else 0} for d in data]
                # If a specific requester filter is provided, return single summary
                if requester_filter and result:
                    return Response(result[0])
                return Response(result)

            return Response({'detail': 'Invalid group_by parameter'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
