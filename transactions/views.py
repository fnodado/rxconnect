from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from transactions.forms import PurchaseTransactionForm, SaleTransactionForm, SaleItemForm, ReturnTransactionForm, \
    ReturnItemForm
from transactions.models import SaleTransaction, ReturnTransaction, PurchaseTransaction, SaleItem


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
def sale_list(request):
    sales = SaleTransaction.objects.select_related('user').all()
    return render(request, 'transactions/sale_transaction_list.html', {'sales': sales})


@login_required
def sale_transaction(request):
    if request.method == 'POST':
        print('sale transaction POST method')
        sale_form = SaleTransactionForm(request.POST, user=request.user)

        if sale_form.is_valid():
            print('sale transaction valid')
            sale = sale_form.save()
            print('sale_id:', sale.sale_id)
            # Redirect to add sale items
            return redirect('sale-item', sale_id=sale.sale_id)
    else:
        sale_form = SaleTransactionForm(user=request.user.id)

    return render(request, 'transactions/sale_transaction.html', {'form': sale_form})

@login_required
def sale_item(request, sale_id):
    sale = get_object_or_404(SaleTransaction, pk=sale_id)
    if request.method == 'POST':
        form = SaleItemForm(request.POST)
        if form.is_valid():
            sale_item = form.save(commit=False)
            sale_item.sale = sale
            print('sale_item.product.unit_price = ', sale_item.product.unit_price)
            sale_item.unit_price = sale_item.product.unit_price
            sale_item.save()
            # Update total price
            sale.total_price += sale_item.sub_total
            sale.save()
            print("sale_item: ", sale_id)
            return redirect('checkout-item', sale_id=sale_id)
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

@login_required
def checkout(request, sale_id):
    print('checkout', sale_id)
    sale = get_object_or_404(SaleTransaction, pk=sale_id)
    sale_items = SaleItem.objects.filter(sale=sale)
    total_price = sum(item.sub_total for item in sale_items)
    return render(request, 'transactions/checkout_items.html', {'sale': sale, 'sale_items': sale_items, 'total_price': total_price, 'sale_id': sale_id})


@login_required
def complete_sale(request, sale_id):
    sale = get_object_or_404(SaleTransaction, pk=sale_id)

    # Update stock for all items in the sale
    sale_items = SaleItem.objects.filter(sale=sale)
    for item in sale_items:
        product = item.product
        if product.current_stock < 0:
            messages.error(request, f"Insufficient stock for product {product.name}")
            return redirect('checkout-item', sale_id=sale_id)
        product.save()

    # Update the sale transaction status
    sale.status = 'completed'
    sale.save()

    messages.success(request, "Transaction completed successfully!")
    # Redirect to the dashboard page
    return redirect('dashboard')


@login_required
def delete_sale_item(request, item_id):
    sale_item = get_object_or_404(SaleItem, pk=item_id)
    sale_id = sale_item.sale.sale_id  # Get associated sale ID

    # Update the sale total price
    sale_item.sale.total_price -= sale_item.sub_total
    sale_item.sale.save()

    # Delete the item
    sale_item.delete()
    messages.success(request, "Item successfully deleted.")
    return redirect('checkout-item', sale_id=sale_id)
