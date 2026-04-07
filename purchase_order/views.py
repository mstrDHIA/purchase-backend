from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer
from rest_framework.response import Response
from purchase_request.models import PurchaseRequest


# Create your views here.


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PurchaseOrder.objects.all()
        requested_by_id = self.request.query_params.get('requested_by')
        if requested_by_id:
            queryset = queryset.filter(requested_by_id=requested_by_id)
        pr_id = self.request.query_params.get('purchase_request_id')
        if pr_id:
            queryset = queryset.filter(purchase_request_id=pr_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def bulk_create_from_pr(self, request):
        """Crée plusieurs PO à partir d'une PR"""
        pr_id = request.data.get('purchase_request_id')
        po_data_list = request.data.get('purchase_orders', [])
        
        try:
            pr = PurchaseRequest.objects.get(id=pr_id)
        except PurchaseRequest.DoesNotExist:
            return Response({'error': 'PurchaseRequest not found'}, status=status.HTTP_404_NOT_FOUND)
        
        created_pos = []
        for po_data in po_data_list:
            po_data['purchase_request'] = pr.id
            serializer = self.get_serializer(data=po_data)
            if serializer.is_valid():
                serializer.save()
                created_pos.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(created_pos, status=status.HTTP_201_CREATED)




