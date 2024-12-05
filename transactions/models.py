from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models

from inventory.models import Product, Supplier


# Purchase Transaction Model
class PurchaseTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Update product stock on purchase
        self.product.current_stock += self.quantity
        self.product.save()
        super().save(*args, **kwargs)

# Sale Transaction Model
class SaleTransaction(models.Model):
    sale_id = models.AutoField(primary_key=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

class SaleItem(models.Model):
    sale_item_id = models.AutoField(primary_key=True)
    sale = models.ForeignKey(SaleTransaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Update product stock on sale
        self.product.current_stock -= self.quantity
        self.product.save()
        # Calculate subtotal
        self.sub_total = self.quantity * self.product.unit_price
        super().save(*args, **kwargs)


# Return Transaction Model
class ReturnTransaction(models.Model):
    return_id = models.AutoField(primary_key=True)
    sale = models.ForeignKey(SaleTransaction, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_reason = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])

class ReturnItem(models.Model):
    return_item_id = models.AutoField(primary_key=True)
    return_transaction = models.ForeignKey(ReturnTransaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Update product stock on return
        self.product.current_stock += self.quantity
        self.product.save()
        # Calculate subtotal
        self.sub_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
