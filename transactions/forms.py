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
        fields = ['refund_reason']

    def __init__(self, *args, **kwargs):
        self.current_sale = kwargs.pop('sale', None)
        self.current_user = kwargs.pop('user', None)
        super(ReturnTransactionForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def save(self, commit=True):
        # Save logic to ensure the field is set properly in the instance
        instance = super(ReturnTransactionForm, self).save(commit=False)
        if self.current_sale:
            instance.sale = self.current_sale  # Explicitly set the value
        if self.current_user:
            instance.user = self.current_user
        if commit:
            instance.save()
        return instance

class ReturnItemForm(forms.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        self.current_quantity = kwargs.pop('quantity', None)
        self.valid_refund_amount = kwargs.pop('valid_refund_amount', None)
        super(ReturnItemForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        print('cleaned quantitiy', quantity)
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        if quantity > self.current_quantity:
            raise forms.ValidationError("Quantity must be less than or equal to the sale item quantity")
        return quantity

    def save(self, commit=True):
        # Save logic to ensure the field is set properly in the instance
        instance = super(ReturnItemForm, self).save(commit=False)
        if self.product:
            instance.product = self.product  # Explicitly set the value
        if commit:
            instance.save()
        return instance
