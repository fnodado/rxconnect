from django import forms

from .models import PurchaseTransaction, ReturnTransaction, ReturnItem
from .models import SaleItem
from .models import SaleTransaction


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





class SaleTransactionForm(forms.ModelForm):
    class Meta:
        model = SaleTransaction
        fields = ['customer_name']

    # user = forms.BooleanField(
    #     widget=forms.TextInput(attrs={'type': 'text', 'class': 'custom-text-input', 'readonly': 'readonly'})  # Change from checkbox to input
    # )

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('user', None)
        super(SaleTransactionForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def save(self, commit=True):
        print('form save ', self.current_user)
        # Save logic to ensure the field is set properly in the instance
        instance = super(SaleTransactionForm, self).save(commit=False)
        if self.current_user:
            instance.user = self.current_user  # Explicitly set the value
        if commit:
            instance.save()
        return instance


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']

        unit_price = forms.BooleanField(
            widget=forms.TextInput(attrs={'readonly': 'readonly'})  # Change from checkbox to input
        )

    def __init__(self, *args, **kwargs):
        super(SaleItemForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        if product:
            cleaned_data['unit_price'] = product.unit_price
        return cleaned_data


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