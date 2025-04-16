from django.db import models
from django.utils import timezone
from datetime import date

class Product2(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)  

    def __str__(self):
        return self.name
    
class Production2(models.Model):
    product = models.ForeignKey(Product2, on_delete=models.CASCADE, related_name='productions')
    date = models.DateField(default=timezone.now)
    quantity_added = models.IntegerField()

    def save(self, *args, **kwargs):
        # Update product quantity before saving production
        self.product.quantity += self.quantity_added
        self.product.save()
        super().save(*args, **kwargs)

class ProductionHistory2(models.Model):
    product = models.ForeignKey(Product2, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    quantity_produced = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity_produced} on {self.date}"

class Customer2(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100,blank=True)

    def __str__(self):
        return self.name
    

class Invoice2(models.Model):
    date = models.DateField()
    customer = models.CharField(max_length=100) 
    location = models.ForeignKey(Customer2, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)  # Allow blank to generate in save()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    accessory_quantity = models.IntegerField(default=0)
    accessory_price= models.IntegerField(default=0)
    e_way = models.IntegerField(default=0)
    sp_discount =models.IntegerField(default=0)
    money_got = models.IntegerField(default=0)
    balance_amount = models.IntegerField(default=0)
    original_money_got = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def final_amount(self):
        discount_amount = (self.total_amount - self.accessory_price) * (self.discount_percentage / 100)
        return (self.total_amount - discount_amount) + self.accessory_price + self.e_way - self.sp_discount

    def save(self, *args, **kwargs):
        if not self.invoice_number:  # Generate invoice number only if it's empty
            last_invoice = Invoice2.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])  # Extract last number
                new_number = f"INV-{self.date.strftime('%d%m%y')}-{last_number + 1:03d}"
            else:
                new_number = f"INV-{self.date.strftime('%d%m%y')}-001"
            self.invoice_number = new_number

        # Automatically calculate the balance amount
        self.balance_amount = self.total_amount - self.money_got
        
        # Save the instance
        super().save(*args, **kwargs)

    def update_payment_totals(self):
        """
        Update the total payment-related fields like balance_amount and money_got
        after a payment has been made for the invoice.
        """
        # Recalculate balance_amount based on the current total_amount and money_got
        self.balance_amount = self.total_amount - self.money_got
        
        # Save the updated invoice
        self.save()

    def __str__(self):
        return self.invoice_number
    
class InvoiceItem2(models.Model):
    invoice = models.ForeignKey(Invoice2, on_delete=models.CASCADE, related_name='invoice_items')
    product = models.ForeignKey(Product2, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add default value
 

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"

class reg2(models.Model):
    name = models.CharField(max_length=20)
    phno = models.CharField(max_length=15)  
    
class login2(models.Model):
    uname = models.CharField(max_length=20)
    pswd = models.CharField(max_length=128)  
    utype = models.CharField(max_length=20)
    uid = models.ForeignKey(reg2, on_delete=models.CASCADE)

class Factorysale2(models.Model):
    date = models.DateField(default=date.today)  # Auto-set to today's date
    flavor = models.CharField(max_length=100)  # Flavor name
    quantity = models.PositiveIntegerField()  # Quantity sold
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total price

    def __str__(self):
        return f"{self.flavor} - {self.quantity} sold on {self.date}"

class PaymentRecord2(models.Model):
    invoice = models.ForeignKey(Invoice2, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    mode = models.CharField(max_length=100, blank=True)  # Optional: UPI/Cash/etc.

    def __str__(self):
        return f"₹{self.amount} on {self.date} for {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.update_payment_totals() 
