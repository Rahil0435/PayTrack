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
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)  # Allow blank to generate in save()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    accessory_required = models.BooleanField(default=False)
    accessory_quantity = models.IntegerField(default=0)

    def final_amount(self):
        discount_amount = (self.total_amount * self.discount_percentage) / 100  # Calculate discount
        return self.total_amount - discount_amount 

    def save(self, *args, **kwargs):
        if not self.invoice_number:  # Generate invoice number only if it's empty
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])  # Extract last number
                new_number = f"INV-{self.date.strftime('%d%m%y')}-{last_number + 1:03d}"
            else:
                new_number = f"INV-{self.date.strftime('%d%m%y')}-001"
            self.invoice_number = new_number

        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    accessory_name = models.CharField(max_length=100, null=True, blank=True) 
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