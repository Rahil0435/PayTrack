from django import forms
from .models import Product,Production,Invoice, InvoiceItem,Factorysale,Customer
from django.utils import timezone
from datetime import timezone

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
        fields = ['customer', 'discount_percentage', 'date','accessory_quantity','accessory_price','sp_discount','e_way','advance_used']
        widgets = {
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'value': '0', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def save(self, commit=True):
        # Call the parent save method without committing it to the database
        invoice = super().save(commit=False)

        # If the date field is not provided, set it to today's date
        if not invoice.date:
            invoice.date = timezone.now().date()  # Default to the current date if not provided

        # Save the instance to the database
        if commit:
            invoice.save()

        return invoice


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'product-select'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'quantity-input'}),
        }


class InvoiceWithItemsForm(forms.Form):
    customer = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    invoice_number = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    discount_percentage = forms.DecimalField(min_value=0, max_value=100, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    products = forms.CharField(widget=forms.HiddenInput(), required=False)  # Store product IDs dynamically
    quantities = forms.CharField(widget=forms.HiddenInput(), required=False)  # Store quantities dynamically

    def clean(self):
        cleaned_data = super().clean()
        products = cleaned_data.get("products", "")
        quantities = cleaned_data.get("quantities", "")

        if not products or not quantities:
            raise forms.ValidationError("Please add at least one product.")

        return cleaned_data

class FactorySaleForm(forms.ModelForm):
    class Meta:
        model = Factorysale
        fields = ['flavor', 'quantity', 'total_amount']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'state','advance_amount']

class MoneyUpdateForm2(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['money_got']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.balance_amount = instance.total_amount - instance.money_got
        if commit:
            instance.save()
        return instance