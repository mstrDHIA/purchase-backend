from django.db import models

# Create your models here.
class Supplier(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        
    ]
    
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    matricule_fiscale = models.CharField(max_length=100, blank=True, null=True)
    cin=models.CharField(max_length=100, blank=True, null=True)
    code_fournisseur=models.CharField(max_length=100, blank=True, null=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.name


class SupplierStat(models.Model):
    """Daily aggregated statistics for a supplier (optional precomputed table)."""
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, related_name='stats')
    date = models.DateField()
    total_spend = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    orders_count = models.IntegerField(default=0)
    avg_order = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    by_subcategory = models.JSONField(blank=True, null=True, help_text='{"subcategory_id": {"name": str, "total": float, "orders": int}}')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('supplier', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.supplier.name} - {self.date.isoformat()}"
