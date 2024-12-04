from django import forms

from inventory.models import Product, Supplier
from .models import PurchaseTransaction, ReturnTransaction, ReturnItem


class PurchaseTransactionForm(forms.ModelForm):
    class Meta:
        model = PurchaseTransaction
        fields = ['product', 'supplier', 'quantity', 'description']

    def __init__(self, *args, **kwargs):
        super(PurchaseTransactionForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity



from django import forms
from .models import SaleTransaction

class SaleTransactionForm(forms.ModelForm):
    class Meta:
        model = SaleTransaction
        fields = ['customer_name', 'user']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }


from django import forms
from .models import SaleItem

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Enter quantity'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter unit price'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return unit_price

class ReturnTransactionForm(forms.ModelForm):
    class Meta:
        model = ReturnTransaction
        fields = ['sale', 'refund_amount', 'refund_reason', 'status']
        widgets = {
            'sale': forms.Select(attrs={'class': 'form-control'}),
            'refund_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter refund amount'}),
            'refund_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter refund reason'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_refund_amount(self):
        refund_amount = self.cleaned_data.get('refund_amount')
        if refund_amount <= 0:
            raise forms.ValidationError("Refund amount must be greater than zero.")
        return refund_amount

class ReturnItemForm(forms.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Enter quantity'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter unit price'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return unit_price