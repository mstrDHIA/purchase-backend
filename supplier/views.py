from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, Value, DecimalField, IntegerField
from django.db.models.functions import Coalesce

from .models import Supplier
from .recommendation import recommend_suppliers
from .serializers import SupplierSerializer, SupplierRecommendationSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='recommendations')
    def recommendations(self, request):
        top = request.query_params.get('top', 5)
        days = request.query_params.get('days')
        supplier_id = request.query_params.get('supplier_id')

        try:
            top = int(top)
        except (TypeError, ValueError):
            top = 5

        try:
            supplier_id = int(supplier_id) if supplier_id is not None else None
        except (TypeError, ValueError):
            supplier_id = None

        try:
            days = int(days) if days is not None else None
        except (TypeError, ValueError):
            days = None

        suppliers = recommend_suppliers(top=top, days=days, supplier_id=supplier_id)

        # Annotate with computed fields for serialization
        supplier_ids = [s.id for s in suppliers]
        stats_filter = Q()
        if days is not None:
            from django.utils import timezone
            from datetime import timedelta
            since_date = timezone.now().date() - timedelta(days=days)
            stats_filter = Q(stats__date__gte=since_date)

        annotated_suppliers = Supplier.objects.filter(id__in=supplier_ids).annotate(
            total_spend=Coalesce(Sum('stats__total_spend', filter=stats_filter), Value(0, output_field=DecimalField())),
            orders_count=Coalesce(Sum('stats__orders_count', filter=stats_filter), Value(0, output_field=IntegerField())),
            score=Coalesce(Sum('stats__total_spend', filter=stats_filter), Value(0, output_field=DecimalField())),
        )

        serializer = SupplierRecommendationSerializer(annotated_suppliers, many=True)
        return Response(serializer.data)