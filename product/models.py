from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subcategory = models.ForeignKey('category.Category', on_delete=models.CASCADE, related_name='products', limit_choices_to={'parent_category__isnull': False})
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
