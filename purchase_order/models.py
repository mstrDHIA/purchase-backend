from django.db import models

# Create your models here.
class PurchaseOrder(models.Model):
    id = models.IntegerField(primary_key=True,unique=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, 
    #                           choices=[
    #     ('pending', 'Pending'),
    #     ('edited', 'Edited'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected'),
    #     ('terminated', 'Terminated')
    # ], 
    default='pending'),
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
    # purchase_request = models.OneToOneField(
    #     'purchase_request.PurchaseRequest', on_delete=models.CASCADE, related_name='purchase_order', blank=True, null=True)
    purchase_request = models.ForeignKey(
        'purchase_request.PurchaseRequest', on_delete=models.CASCADE, related_name='purchase_orders', blank=True, null=True)
    is_archived = models.BooleanField(default=False)    
    # purchase_request = models.ForeignKey(
    #     'purchase_request.PurchaseRequest', on_delete=models.CASCADE, related_name='purchase_orders', blank=True, null=True)
    supplier_delivery_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class PurchaseOrderLine(models.Model):
    """Modèle pour gérer chaque ligne d'un Purchase Order avec son propre statut"""
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='order_lines'
    )
    product = models.ForeignKey(
        'product.Product', on_delete=models.CASCADE, related_name='purchase_order_lines'
    )
    supplier = models.ForeignKey(
        'supplier.Supplier', on_delete=models.CASCADE, related_name='purchase_order_lines'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Statut individuel de la ligne
    status = models.CharField(max_length=20, choices=[
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('partially_approved', 'Partiellement approuvé')
    ], default='pending')
    
    # Gestion de l'approbation/rejet
    approved_by = models.ForeignKey(
        'custom_user.User', on_delete=models.SET_NULL, 
        related_name='approved_lines', blank=True, null=True
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    
    rejected_by = models.ForeignKey(
        'custom_user.User', on_delete=models.SET_NULL, 
        related_name='rejected_lines', blank=True, null=True
    )
    rejected_at = models.DateTimeField(blank=True, null=True)
    rejected_reason = models.ForeignKey(
        'reject_reasons.RejectReason', on_delete=models.SET_NULL, 
        related_name='rejected_lines', blank=True, null=True
    )
    reject_comment = models.TextField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ['purchase_order', 'product', 'supplier']

    def __str__(self):
        return f"{self.purchase_order.title} - {self.product.name} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        # Calcul automatique du prix total
        if self.quantity and self.unit_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class PurchaseOrderLine(models.Model):
    """Modèle pour gérer chaque ligne d'un Purchase Order avec son propre statut"""
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name='lines'
    )
    product = models.ForeignKey(
        'product.Product', on_delete=models.CASCADE, related_name='purchase_order_lines'
    )
    supplier = models.ForeignKey(
        'supplier.Supplier', on_delete=models.CASCADE, related_name='purchase_order_lines'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Statut individuel de la ligne
    status = models.CharField(max_length=20, choices=[
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('partially_approved', 'Partiellement approuvé')
    ], default='pending')
    
    # Gestion de l'approbation/rejet
    approved_by = models.ForeignKey(
        'custom_user.User', on_delete=models.SET_NULL, 
        related_name='approved_lines', blank=True, null=True
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    
    rejected_by = models.ForeignKey(
        'custom_user.User', on_delete=models.SET_NULL, 
        related_name='rejected_lines', blank=True, null=True
    )
    rejected_at = models.DateTimeField(blank=True, null=True)
    rejected_reason = models.ForeignKey(
        'reject_reasons.RejectReason', on_delete=models.SET_NULL, 
        related_name='rejected_lines', blank=True, null=True
    )
    reject_comment = models.TextField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ['purchase_order', 'product', 'supplier']

    def __str__(self):
        return f"{self.purchase_order.title} - {self.product.name} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        # Calcul automatique du prix total
        if self.quantity and self.unit_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
