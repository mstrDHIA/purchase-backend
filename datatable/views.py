from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from statistic.views import get_filtered_purchase_orders
from purchase_order.serializers import PurchaseOrderSerializer


class POListView(APIView):
    """Return all PurchaseOrders matching the current filters without pagination by default.
    
    Supports `page` and `page_size` GET params:
    - If page_size is omitted or 0: return ALL results at once
    - If page_size > 0: return paginated results (page_size items per page)
    """

    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            # default to 0 = return all; if explicitly set, honor the value
            page_size_param = request.GET.get('page_size')
            page_size = int(page_size_param) if page_size_param else 0
            
            # return_all if page_size not specified or is 0
            return_all = (page_size <= 0)
            if page < 1:
                page = 1

            qs_or_list = get_filtered_purchase_orders(request, include_status_filter=True)

            # determine total and slice
            if isinstance(qs_or_list, list):
                total = len(qs_or_list)
                if return_all:
                    page_items = qs_or_list
                else:
                    start = (page - 1) * page_size
                    end = start + page_size
                    page_items = qs_or_list[start:end]
            else:
                total = qs_or_list.count()
                if return_all:
                    page_items = qs_or_list.order_by('-created_at')
                else:
                    start = (page - 1) * page_size
                    end = start + page_size
                    page_items = qs_or_list.order_by('-created_at')[start:end]

            serializer = PurchaseOrderSerializer(page_items, many=True)
            response_page_size = total if return_all else page_size
            return Response({'total': total, 'page': page, 'page_size': response_page_size, 'results': serializer.data})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
