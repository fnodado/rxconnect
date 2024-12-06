from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from inventory.models import Product
from transactions.forms import PurchaseTransactionForm, SaleTransactionForm, SaleItemForm, ReturnTransactionForm, \
    ReturnItemForm
from transactions.models import SaleTransaction, ReturnTransaction, PurchaseTransaction, SaleItem, ReturnItem


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
def return_transaction(request, sale_id):
    sale_transaction_obj = get_object_or_404(SaleTransaction, pk=sale_id)

    if request.method == 'POST':
        form = ReturnTransactionForm(request.POST, sale=sale_transaction_obj,
                                     user=request.user)
        if form.is_valid():
            print('valid')
            return_transaction_obj = form.save()
            print('saved')
            return redirect('view-sale-items', sale_id, return_transaction_obj.return_id)  # Redirect to the sale transaction given id
    else:
        print('else statemeent', sale_item)
        form = ReturnTransactionForm(initial={
            'sale': sale_transaction_obj,
        })

    return render(request, 'transactions/return_transaction.html', {
        'form': form,
    })
@login_required
def return_item(request, return_id, sale_item_id):
    sale_item_obj = get_object_or_404(SaleItem, pk=sale_item_id)
    product = get_object_or_404(Product, pk=sale_item_obj.product_id)
    return_transaction_obj = get_object_or_404(ReturnTransaction, pk=return_id)
    print('sale item qty: ', sale_item_obj.quantity)
    print('product in return: ', product)
    print('product type: ', type(product))
    print('product instance: ', product)
    if request.method == 'POST':
        print('request method post')
        form = ReturnItemForm(request.POST, quantity=sale_item_obj.quantity,
                                     valid_refund_amount=sale_item_obj.unit_price,
                                    product= product)
        if form.is_valid():
            print('return valid form')
            return_item_obj = form.save(commit=False)
            return_item_obj.return_transaction = return_transaction_obj
            return_item_obj.save()
            return redirect('return-checkout-item', return_id=return_id)

    else:
        form = ReturnItemForm()
    return render(request, 'transactions/return_item.html',
                  {'form': form, 'product': product})

@login_required
def checkout(request, sale_id):
    print('checkout', sale_id)
    sale = get_object_or_404(SaleTransaction, pk=sale_id)
    sale_items = SaleItem.objects.filter(sale=sale)
    total_price = sum(item.sub_total for item in sale_items)
    return render(request, 'transactions/checkout_items.html', {'sale': sale, 'sale_items': sale_items, 'total_price': total_price, 'sale_id': sale_id})

@login_required
def return_checkout(request, return_id):
    print('refund checkout', return_id)
    return_transaction_obj = get_object_or_404(ReturnTransaction, pk=return_id)
    print('got the rreturn object')
    return_items = ReturnItem.objects.filter(return_transaction=return_transaction_obj)
    print('got he return_items', return_items)
    total_price = sum(item.sub_total for item in return_items)
    return render(request, 'transactions/return_checkout_items.html', {'return_transaction': return_transaction_obj, 'return_items': return_items,
                'total_price': total_price, 'sale_id': return_transaction_obj.sale_id, 'return_id': return_id})

@login_required
def complete_return(request, return_id):
    print('complete_return')
    return_transaction_obj = get_object_or_404(ReturnTransaction, pk=return_id)

    # Update stock for all items in the sale
    return_items = ReturnItem.objects.filter(return_transaction=return_transaction_obj)
    for item in return_items:
        product = item.product

        product.current_stock += item.quantity
        product.save()

    # Update the sale transaction status
    return_transaction_obj.status = 'completed'
    return_transaction_obj.save()

    messages.success(request, "Transaction completed successfully!")
    # Redirect to the dashboard page
    return redirect('dashboard')


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

@login_required
def delete_return_item(request, return_item_id):
    return_item_obj = get_object_or_404(ReturnItem, pk=return_item_id)
    return_id = return_item_obj.return_transaction.return_id  # Get associated sale ID


    # Delete the item
    return_item_obj.delete()
    messages.success(request, "Item successfully deleted.")
    return redirect('return-checkout-item', return_id=return_id)


@login_required
def view_sale_items(request, sale_id, return_id):
    print('view sale item return id', return_id)
    print('view sale item sale id', sale_id)
    sale = get_object_or_404(SaleTransaction, pk=sale_id)
    print('here')
    sale_items = SaleItem.objects.filter(sale=sale)
    print('before html')
    return render(request, 'transactions/view_sale_items.html', {'sale': sale,
                    'sale_items': sale_items, 'return_id': return_id, 'sale_id': sale_id})
