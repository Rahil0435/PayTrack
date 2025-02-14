from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)  

    def __str__(self):
        return self.name
    
class Production(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productions')
    date = models.DateField(default=timezone.now)
    quantity_added = models.IntegerField()

    def save(self, *args, **kwargs):
        # Update product quantity before saving production
        self.product.quantity += self.quantity_added
        self.product.save()
        super().save(*args, **kwargs)

class ProductionHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    quantity_produced = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity_produced} on {self.date}"


class Invoice(models.Model):
    date = models.DateField()
    customer = models.CharField(max_length=30, default="Unknown Customer")
    invoice_number = models.CharField(max_length=20, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def final_amount(self):
        discount_amount = (self.total_amount * self.discount_percentage) / 100  # Calculate discount
        return self.total_amount - discount_amount 

    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add default value
 

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"

class reg(models.Model):
    name = models.CharField(max_length=20)
    phno = models.CharField(max_length=15)  
    
class login(models.Model):
    uname = models.CharField(max_length=20)
    pswd = models.CharField(max_length=128)  
    utype = models.CharField(max_length=20)
    uid = models.ForeignKey(reg, on_delete=models.CASCADE)