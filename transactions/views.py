from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from transactions.forms import PurchaseTransactionForm, SaleTransactionForm, SaleItemForm, ReturnTransactionForm, \
    ReturnItemForm
from transactions.models import SaleTransaction, ReturnTransaction, PurchaseTransaction


# Create your views here.
@login_required
def purchase_list(request):
    purchases = PurchaseTransaction.objects.all()
    return render(request, 'transactions/purchase_transaction_list.html', {'purchases': purchases})

@login_required
def purchase_transaction(request):
    if request.method == 'POST':
        form = PurchaseTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('purchase-list')
    else:
        form = PurchaseTransactionForm()
    return render(request, 'transactions/add_edit_purchase.html', {'form': form, 'page': 'add_purchase'})

@login_required
def sale_transaction(request):
    if request.method == 'POST':
        sale_form = SaleTransactionForm(request.POST)
        if sale_form.is_valid():
            sale = sale_form.save()
            # Redirect to add sale items
            return redirect('sale-item', sale_id=sale.sale_id)
    else:
        sale_form = SaleTransactionForm()
    return render(request, 'transactions/sale_transaction.html', {'sale_form': sale_form})

@login_required
def sale_item(request, sale_id):
    sale = get_object_or_404(SaleTransaction, pk=sale_id)
    if request.method == 'POST':
        form = SaleItemForm(request.POST)
        if form.is_valid():
            sale_item = form.save(commit=False)
            sale_item.sale = sale
            sale_item.save()
            # Update total price
            sale.total_price += sale_item.sub_total
            sale.save()
            return redirect('sale-item', sale_id=sale_id)
    else:
        form = SaleItemForm()
    return render(request, 'transactions/sale_item.html', {'form': form, 'sale': sale})

@login_required
def return_transaction(request):
    if request.method == 'POST':
        form = ReturnTransactionForm(request.POST)
        if form.is_valid():
            return_transaction = form.save()
            return redirect('return-item', return_id=return_transaction.return_id)
    else:
        form = ReturnTransactionForm()
    return render(request, 'transactions/return_transaction.html', {'form': form})

@login_required
def return_item(request, return_id):
    return_transaction = get_object_or_404(ReturnTransaction, pk=return_id)
    if request.method == 'POST':
        form = ReturnItemForm(request.POST)
        if form.is_valid():
            return_item = form.save(commit=False)
            return_item.return_transaction = return_transaction
            return_item.save()
            return redirect('return-item', return_id=return_id)
    else:
        form = ReturnItemForm()
    return render(request, 'transactions/return_item.html', {'form': form, 'return_transaction': return_transaction})

