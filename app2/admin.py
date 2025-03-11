from django.contrib import admin
from .models import Invoice2,reg2,ProductionHistory2,Product2,InvoiceItem2,login2,Production2,Factorysale2

# Register your models here.
    
@admin.register(Product2)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity') 

@admin.register(Invoice2)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'date', 'total_amount','e_way', 'final_amount') 
@admin.register(reg2)  
class regAdmin(admin.ModelAdmin):
    list_display = ('name',  'phno')
@admin.register(login2)
class loginAdmin(admin.ModelAdmin):
    list_display = ('uname', 'pswd')

@admin.register(Production2)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ( 'product', 'quantity_added')

@admin.register(InvoiceItem2)
class InvoiceitemAdmin(admin.ModelAdmin):
    list_display=('product','quantity')

@admin.register(ProductionHistory2)
class productionhitoryAdmin(admin.ModelAdmin):
    list_display=('product', 'quantity_produced','date')

@admin.register(Factorysale2)
class FactorysaleAdmin(admin.ModelAdmin):
    list_display=('flavor', 'quantity', 'total_amount','date')