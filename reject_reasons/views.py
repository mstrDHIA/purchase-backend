from rest_framework import viewsets, permissions

from reject_reasons.models import RejectReason
from reject_reasons.serializers import RejectReasonSerializer

# Create your views here.

class RejectReasonViewSet(viewsets.ModelViewSet):
    queryset = RejectReason.objects.all()
    serializer_class = RejectReasonSerializer
    permission_classes = [permissions.IsAuthenticated]
