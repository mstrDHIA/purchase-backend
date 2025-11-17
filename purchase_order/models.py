from django.db import models

# Create your models here.
class PurchaseOrder(models.Model):
    id = models.IntegerField(primary_key=True,unique=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    approved_by_user = models.ForeignKey(
        'custom_user.User', on_delete=models.CASCADE, related_name='approved_by_user', blank=True, null=True)
    products = models.JSONField(blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    requested_by_user = models.ForeignKey(
        'custom_user.User', on_delete=models.CASCADE, related_name='requested_by_user')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
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


    def __str__(self):
        return self.title
