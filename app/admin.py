from django.contrib import admin
from .models import Invoice,reg,ProductionHistory,Product,InvoiceItem,login,Production

# Register your models here.
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity') 

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'date', 'total_amount') 
@admin.register(reg)  
class regAdmin(admin.ModelAdmin):
    list_display = ('name',  'phno')
@admin.register(login)
class loginAdmin(admin.ModelAdmin):
    list_display = ('uname', 'pswd')

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ( 'product', 'quantity_added')
