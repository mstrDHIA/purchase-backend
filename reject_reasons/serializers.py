

from rest_framework import serializers

from reject_reasons.models import RejectReason


class RejectReasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = RejectReason
        fields = '__all__'