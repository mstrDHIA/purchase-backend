from django.db import models

# Create your models here.

class PurchaseRequest(models.Model):
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    approved_by = models.ForeignKey(
        'custom_user.User', on_delete=models.CASCADE, related_name='approved_by')
    products = models.JSONField(blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    requested_by = models.ForeignKey(
        'custom_user.User', on_delete=models.CASCADE, related_name='requested_by')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.title
