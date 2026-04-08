from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import PurchaseOrder, PurchaseOrderLine
from .serializers import PurchaseOrderSerializer, PurchaseOrderLineSerializer
from rest_framework.response import Response


# Create your views here.


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PurchaseOrder.objects.all()
        requested_by_id = self.request.query_params.get('requested_by')
        if requested_by_id:
            queryset = queryset.filter(requested_by_id=requested_by_id)
        return queryset


class PurchaseOrderLineViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les lignes de Purchase Order"""
    serializer_class = PurchaseOrderLineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PurchaseOrderLine.objects.all()
        purchase_order_id = self.request.query_params.get('purchase_order')
        if purchase_order_id:
            queryset = queryset.filter(purchase_order_id=purchase_order_id)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver une ligne spécifique"""
        line = self.get_object()
        
        # Vérifier les permissions (seulement user ID 6 peut approuver)
        if request.user.id != 6:
            return Response(
                {"error": "Vous n'avez pas la permission d'approuver cette ligne."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que la ligne n'est pas déjà approuvée
        if line.status == 'approved':
            return Response(
                {"error": "Cette ligne est déjà approuvée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Approuver la ligne
        line.status = 'approved'
        line.approved_by = request.user
        line.approved_at = timezone.now()
        line.save()
        
        # Mettre à jour le statut du PO si nécessaire
        self._update_purchase_order_status(line.purchase_order)
        
        serializer = self.get_serializer(line)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter une ligne spécifique"""
        line = self.get_object()
        
        # Vérifier les permissions (seulement user ID 6 peut rejeter)
        if request.user.id != 6:
            return Response(
                {"error": "Vous n'avez pas la permission de rejeter cette ligne."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que la ligne n'est pas déjà rejetée
        if line.status == 'rejected':
            return Response(
                {"error": "Cette ligne est déjà rejetée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les données de rejet
        rejected_reason_id = request.data.get('rejected_reason')
        reject_comment = request.data.get('reject_comment', '')
        
        if not rejected_reason_id:
            return Response(
                {"error": "La raison du rejet est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rejeter la ligne
        line.status = 'rejected'
        line.rejected_by = request.user
        line.rejected_at = timezone.now()
        line.rejected_reason_id = rejected_reason_id
        line.reject_comment = reject_comment
        line.save()
        
        # Mettre à jour le statut du PO si nécessaire
        self._update_purchase_order_status(line.purchase_order)
        
        serializer = self.get_serializer(line)
        return Response(serializer.data)

    def _update_purchase_order_status(self, purchase_order):
        """Mettre à jour le statut global du Purchase Order basé sur ses lignes"""
        lines = purchase_order.order_lines.all()
        
        if not lines.exists():
            return
        
        # Compter les statuts
        approved_count = lines.filter(status='approved').count()
        rejected_count = lines.filter(status='rejected').count()
        pending_count = lines.filter(status='pending').count()
        total_lines = lines.count()
        
        # Logique de calcul du statut global
        if rejected_count > 0 and approved_count == 0:
            # Toutes les lignes rejetées
            new_status = 'rejected'
        elif approved_count == total_lines:
            # Toutes les lignes approuvées
            new_status = 'approved'
        elif approved_count > 0 and rejected_count > 0:
            # Mélange approuvé/rejeté
            new_status = 'partially_approved'
        else:
            # En attente
            new_status = 'pending'
        
        # Mettre à jour le statut du PO
        purchase_order.status = new_status
        purchase_order.save()




