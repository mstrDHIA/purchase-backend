from django.db import models
from django.db.models import Max

# Create your models here.
class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Auto-généré: PR_ID-1, PR_ID-2
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('edited', 'Edited'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('terminated', 'Terminated')
        ],
        default='pending'
    )
    approved_by_user = models.ForeignKey(
        'custom_user.User', on_delete=models.CASCADE, related_name='approved_by_user', blank=True, null=True)
    products = models.JSONField(blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    requested_by_user = models.ForeignKey(
        'custom_user.User', on_delete=models.CASCADE, related_name='requested_by_user')
    # Optional explicit department on the PurchaseOrder itself to allow
    # filtering/grouping by department without relying only on the requester profile.
    department = models.ForeignKey(
        'department.Department', on_delete=models.SET_NULL,
        related_name='purchase_orders_by_department', blank=True, null=True)
    rejected_reason = models.ForeignKey(
        'reject_reasons.RejectReason', on_delete=models.CASCADE, related_name='rejected_reason', blank=True, null=True)
    
    currency = models.CharField(max_length=10, blank=True, null=True, default='TND',
                                choices=[
    ('TND', 'TND'),
    ('USD', 'USD'),
    ('EUR', 'EUR')

    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    refuse_reason = models.TextField(blank=True, null=True)
    purchase_request = models.ForeignKey(
        'purchase_request.PurchaseRequest', on_delete=models.CASCADE, related_name='purchase_orders', blank=True, null=True)
    is_archived = models.BooleanField(default=False)    
    supplier_delivery_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-générer po_number si pas défini et si purchase_request existe
        if not self.po_number and self.purchase_request:
            try:
                # Chercher le nombre de PO existantes pour cette PR
                count = PurchaseOrder.objects.filter(
                    purchase_request=self.purchase_request
                ).count() + 1
                self.po_number = f"{self.purchase_request.id}-{count}"
            except:
                pass  # Si erreur, continuer sans po_number
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_number or self.id} - {self.title}"
