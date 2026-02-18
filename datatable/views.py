from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from statistic.views import get_filtered_purchase_orders
from purchase_order.serializers import PurchaseOrderSerializer


class POListView(APIView):
    """Return a (paginated) list of PurchaseOrders matching the same filters
    used by statistics. Supports `page` and `page_size` GET params.
    """

    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 20

            qs_or_list = get_filtered_purchase_orders(request, include_status_filter=True)

            # determine total and slice
            if isinstance(qs_or_list, list):
                total = len(qs_or_list)
                start = (page - 1) * page_size
                end = start + page_size
                page_items = qs_or_list[start:end]
            else:
                total = qs_or_list.count()
                start = (page - 1) * page_size
                end = start + page_size
                page_items = qs_or_list.order_by('-created_at')[start:end]

            serializer = PurchaseOrderSerializer(page_items, many=True)
            return Response({'total': total, 'page': page, 'page_size': page_size, 'results': serializer.data})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
