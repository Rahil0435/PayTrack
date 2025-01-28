from django import forms
from .models import Product,Production,Invoice, InvoiceItem

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity']

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ['product', 'quantity_added']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['date', 'customer',]
        exclude = ['invoice_number', 'total_amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'product-select'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'quantity-input'}),
        }

class InvoiceWithItemsForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    invoice_number = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter invoice number'}))
    products = forms.CharField(widget=forms.HiddenInput(), required=False)  # To store selected product IDs dynamically
    quantities = forms.CharField(widget=forms.HiddenInput(), required=False)  # To store quantities dynamically