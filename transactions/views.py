from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection, DatabaseError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from inventory.views import get_product_by_id
from transactions.forms import PurchaseTransactionForm, SaleTransactionForm, SaleItemForm, ReturnTransactionForm, \
    ReturnItemForm
from transactions.models import SaleTransaction, ReturnTransaction, SaleItem, ReturnItem


# Create your views here.
@login_required
def purchase_list(request):
    try:
        #with statement in python is used for resource management.
        #It ensures ;actions like opening/closing are handled automatically
        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('rxconnect.get_all_purchases')
            purchase = cursor.fetchall()

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                purchase_list = [dict(zip(columns, row)) for row in purchase]

    except DatabaseError as e:
        # Log the error and return an empty list or error page
        print(f"Database error occurred: {e}")
        purchase_list = []

    # purchases = PurchaseTransaction.objects.all()
    return render(request, 'transactions/purchase_transaction_list.html', {'purchases': purchase_list})

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
    try:
        #with statement in python is used for resource management.
        #It ensures ;actions like opening/closing are handled automatically
        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('rxconnect.get_all_sales')
            sale = cursor.fetchall()

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                sale_list = [dict(zip(columns, row)) for row in sale]

    except DatabaseError as e:
        # Log the error and return an empty list or error page
        print(f"Database error occurred: {e}")
        sale_list = []

    print("sale list: " , sale_list)
    # sales = SaleTransaction.objects.select_related('user').all()
    return render(request, 'transactions/sale_transaction_list.html', {'sales': sale_list})

@login_required
def return_list(request):
    try:
        #with statement in python is used for resource management.
        #It ensures ;actions like opening/closing are handled automatically
        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('rxconnect.get_all_return')
            sale = cursor.fetchall()

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return_list = [dict(zip(columns, row)) for row in sale]

    except DatabaseError as e:
        # Log the error and return an empty list or error page
        print(f"Database error occurred: {e}")
        return_list = []

    print("return list: " , return_list)
    return render(request, 'transactions/return_transaction_list.html', {'return_list': return_list})



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
    sale = get_sale_by_id(sale_id)
    if request.method == 'POST':
        form = SaleItemForm(request.POST)
        if form.is_valid():
            sale_item = form.save(commit=False)
            sale_item.sale = sale
            print('sale_item.product.unit_price = ', sale_item.product.unit_price)
            sale_item.unit_price = sale_item.product.unit_price

            print('sale item: ', sale_item.sale_item_id)
            print('sale item: ', sale_item.quantity)
            print('sale item: ', sale_item.unit_price)
            print('sale item: ', sale_item.sub_total)
            print('sale item: ', sale_item.product_id)
            print('sale item: ', sale_item.sale_id)
            print('sale item: ', sale_item.product)

            if sale_item.product:
                sale_item.product_name = sale_item.product.name
            # Update product stock on sale
            sale_item.product.current_stock -= sale_item.quantity
            sale_item.product.save()
            # Calculate subtotal
            sale_item.sub_total = sale_item.quantity * sale_item.product.unit_price

            save_sale_item(sale_item.sale_item_id, sale_item.quantity, sale_item.unit_price,
                           sale_item.sub_total, sale_item.product_id, sale_item.sale_id,
                           sale_item.product_name)
            # sale_item.save()
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
    print('sale id: ', sale_id)
    sale_transaction_obj = get_sale_by_id(sale_id)

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
    sale_item_obj = get_sale_item_by_id(sale_item_id)
    product = get_product_by_id(sale_item_obj.product_id)
    return_transaction_obj = get_return_by_id(return_id)
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
            return_item_obj.sub_total = return_item_obj.quantity * return_item_obj.product.unit_price
            print('save_return_item: ', return_item_obj.return_item_id)
            print('save_return_item: ', return_item_obj.quantity)
            print('save_return_item: ', return_item_obj.sub_total)
            print('save_return_item: ', return_item_obj.product_id)
            print('save_return_item: ', return_item_obj.return_transaction_id)

            save_return_item(return_item_obj.quantity, return_item_obj.sub_total,
                             return_item_obj.product_id, return_item_obj.return_transaction_id)
            # return_item_obj.save()
            return redirect('return-checkout-item', return_id=return_id)

    else:
        form = ReturnItemForm()
    return render(request, 'transactions/return_item.html',
                  {'form': form, 'product': product})

@login_required
def checkout(request, sale_id):
    print('checkout', sale_id)
    sale = get_sale_by_id(sale_id)
    sale_items = get_sale_items(sale_id)
    total_price = sum(item.sub_total for item in sale_items)
    return render(request, 'transactions/checkout_items.html', {'sale': sale, 'sale_items': sale_items, 'total_price': total_price, 'sale_id': sale_id})

@login_required
def return_checkout(request, return_id):
    print('refund checkout', return_id)
    return_transaction_obj = get_return_by_id(return_id)
    print('got the rreturn object', return_transaction_obj.return_id)
    # return_items = ReturnItem.objects.filter(return_transaction=return_transaction_obj)
    return_items = get_return_items(return_transaction_obj.return_id)
    print('got he return_items', return_items)
    total_price = sum(item.sub_total for item in return_items)
    return render(request, 'transactions/return_checkout_items.html', {'return_transaction': return_transaction_obj, 'return_items': return_items,
                'total_price': total_price, 'sale_id': return_transaction_obj.sale_id, 'return_id': return_id})

@login_required
def complete_return(request, return_id):
    print('complete_return')
    return_transaction_obj = get_return_by_id(return_id)

    # Update stock for all items in the sale
    return_items = get_return_items(return_transaction_obj.return_id)
    for item in return_items:
        product = item.product

        product.current_stock += item.quantity

        print('product.name: ', item.product.product_id)
        print('product.name: ', product.name)
        print('product.name: ', product.unit_price)
        print('product.name: ', product.current_stock)
        print('product.name: ', product.description)
        save_product(item.product.product_id, product.name, product.unit_price, product.current_stock, product.description)
        # product.save()

    # Update the sale transaction status
    return_transaction_obj.status = 'completed'

    print('save_return_transaction: ' , return_transaction_obj.return_id)
    print('save_return_transaction: ' , return_transaction_obj.transaction_date)
    print('save_return_transaction: ' , return_transaction_obj.refund_reason)
    print('save_return_transaction: ' , return_transaction_obj.status)
    print('save_return_transaction: ' , return_transaction_obj.user_id)
    print('save_return_transaction: ' , return_transaction_obj.sale_id)
    save_return_transaction(return_transaction_obj.return_id, return_transaction_obj.transaction_date,
                            return_transaction_obj.refund_reason, return_transaction_obj.status,
                            return_transaction_obj.user_id, return_transaction_obj.sale_id)
    # return_transaction_obj.save()

    sale = get_sale_by_id(return_transaction_obj.sale_id)

    sale.status = 'returned'
    save_sale_transaction(sale.sale_id, sale.transaction_date, sale.customer_name,
                          sale.total_price, sale.user_id, sale.status)

    messages.success(request, "Transaction completed successfully!")
    # Redirect to the dashboard page
    return redirect('dashboard')


@login_required
def complete_sale(request, sale_id):
    sale = get_sale_by_id(sale_id)

    # Update stock for all items in the sale
    sale_items = get_sale_items(sale_id)
    for item in sale_items:
        product = item.product
        if product.current_stock < 0:
            messages.error(request, f"Insufficient stock for product {product.name}")
            return redirect('checkout-item', sale_id=sale_id)

        print('product.name: ', item.product.product_id)
        print('product.name: ', product.name)
        print('product.name: ', product.unit_price)
        print('product.name: ', product.current_stock)
        print('product.name: ', product.description)
        save_product(item.product.product_id, product.name, product.unit_price, product.current_stock, product.description);
        # product.save()

    # Update the sale transaction status
    sale.status = 'completed'
    print('user id:',sale.user_id)
    save_sale_transaction(sale.sale_id, sale.transaction_date, sale.customer_name,
                          sale.total_price, sale.user_id, sale.status)
    # sale.save()

    messages.success(request, "Transaction completed successfully!")
    # Redirect to the dashboard page
    return redirect('dashboard')


@login_required
def delete_sale_item(request, item_id):
    sale_item = get_sale_item_by_id(item_id)
    sale_id = sale_item.sale.sale_id  # Get associated sale ID

    # Update the sale total price
    sale_item.sale.total_price -= sale_item.sub_total
    sale_item.sale.save()

    # Delete the item
    # sale_item.delete()
    delete_sale_item_by_id(sale_item.sale_item_id)
    messages.success(request, "Item successfully deleted.")
    return redirect('checkout-item', sale_id=sale_id)

@login_required
def delete_return_item(request, return_item_id):
    return_item_obj = get_return_item_by_id(return_item_id)
    return_id = return_item_obj.return_transaction.return_id  # Get associated sale ID


    # Delete the item
    # return_item_obj.delete()
    delete_return_item_by_id(return_item_obj.return_item_id)
    messages.success(request, "Item successfully deleted.")
    return redirect('return-checkout-item', return_id=return_id)


@login_required
def view_sale_items(request, sale_id, return_id):
    print('view sale item return id', return_id)
    print('view sale item sale id', sale_id)
    sale = get_sale_by_id(sale_id)
    print('here')
    sale_items = get_sale_items(sale_id)
    print('sale items:', sale_items)
    print('before html')
    return render(request, 'transactions/view_sale_items.html', {'sale': sale,
                    'sale_items': sale_items, 'return_id': return_id, 'sale_id': sale_id})


def get_sale_by_id(sale_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('rxconnect.get_sale_by_id', [sale_id])
            row = cursor.fetchone()

            if not row:
                raise Http404("Sale Transaction does not exist")

            # columns = [col[0] for col in cursor.description]
            # product = dict(zip(columns, row))
            print("here i am")
            sale = SaleTransaction(
                sale_id=row[0],
                transaction_date=row[1],
                customer_name=row[2],
                total_price=row[3],
                user_id=row[4],
                status=row[5]
            )
            print("sale transaction: ", sale)
            return sale

    except Exception as e:
        print(f"Error: {e}")
        raise Http404("Sale Transaction does not exist")

def get_sale_item_by_id(sale_item_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('rxconnect.get_sale_item_by_id', [sale_item_id])
            row = cursor.fetchone()

            if not row:
                raise Http404("Sale Transaction does not exist")

            # columns = [col[0] for col in cursor.description]
            # product = dict(zip(columns, row))
            print("here i am")
            sale = SaleItem(
                sale_item_id=row[0],
                quantity=row[1],
                unit_price=row[2],
                sub_total=row[3],
                product_id=row[4],
                sale_id=row[5],
                product_name=row[6]
            )
            print("sale item: ", sale)
            return sale

    except Exception as e:
        print(f"Error: {e}")
        raise Http404("Sale Item does not exist")


def get_return_by_id(return_id):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('rxconnect.get_return_by_id', [return_id])

            row = cursor.fetchone()

            if not row:
                raise Http404("Return Transaction does not exist")

            # columns = [col[0] for col in cursor.description]
            # product = dict(zip(columns, row))
            print("here i am")
            return_transaction = ReturnTransaction(
                return_id=row[0],
                transaction_date=row[1],
                refund_reason=row[2],
                status=row[3],
                user_id=row[4],
                sale_id=row[5],
            )
            print("return transaction: ", return_transaction)
            return return_transaction

    except Exception as e:
        print(f"Error: {e}")
        raise Http404("Return Transaction does not exist")

def get_return_item_by_id(return_item_id):
    try:
        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('rxconnect.get_return_item_by_id', [return_item_id])

            # Fetch one product
            row = cursor.fetchone()

            if not row:
                raise Http404("Return Item does not exist")

            # columns = [col[0] for col in cursor.description]
            # product = dict(zip(columns, row))
            print("here i am")
            return_item_obj = ReturnItem(
                return_item_id=row[0],
                quantity=row[1],
                sub_total=row[2],
                product_id=row[3],
                return_transaction_id=row[4],
            )
            print("return item: ", return_transaction)
            return return_item_obj

    except Exception as e:
        print(f"Error: {e}")
        raise Http404("Return Item does not exist")

from django.db import connection

def delete_sale_item_by_id(sale_item_id):
    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.delete_sale_item_by_id', [sale_item_id])

def delete_return_item_by_id(return_item_id):
    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.delete_return_item_by_id', [return_item_id])


def get_sale_items(sale_id):

    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.get_sale_items_by_sale_id', [sale_id])
        rows = cursor.fetchall()

    sale_items = [
        SaleItem(sale_item_id=row[0],
                 quantity=row[1],
                 unit_price=row[2],
                 sub_total=row[3],
                 product_id=row[4],
                 sale_id=row[5],
                 product_name=row[6])
        for row in rows
    ]
    return sale_items

def get_return_items(return_transaction_id):

    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.get_return_items_by_transaction_id', [return_transaction_id])
        rows = cursor.fetchall()

    return_transaction_items = [
        ReturnItem(return_item_id=row[0],
                 quantity=row[1],
                 sub_total=row[2],
                 product_id=row[3],
                 return_transaction_id=row[4],
                 )
        for row in rows
    ]
    return return_transaction_items

def save_product(product_id, product_name, product_price, current_stock, product_description):
    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.save_product', [
            product_id,
            product_name,
            product_price,
            current_stock,
            product_description
        ])

def save_sale_transaction(sale_id, transaction_date, customer_name, total_price, user_id, status):
    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.save_sale_transaction', [
            sale_id,
            transaction_date,
            customer_name,
            total_price,
            user_id,
            status
        ])

def save_sale_item(sale_item_id, quantity_param, unit_price_param, sub_total_param, product_id_param, sale_id_param, product_name_param):
    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.save_sale_item', [
            sale_item_id,
            quantity_param,
            unit_price_param,
            sub_total_param,
            product_id_param,
            sale_id_param,
            product_name_param
        ])

def save_return_item(quantity_param, sub_total_param, product_id_param, return_transaction_id_param):
    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.save_return_item', [
            quantity_param,
            sub_total_param,
            product_id_param,
            return_transaction_id_param
        ])

def save_return_transaction(return_id_param, transaction_date_param, refund_reason_param, status_param, user_id_param, sale_id_param):
    with connection.cursor() as cursor:
        cursor.callproc('rxconnect.save_return_transaction', [
            return_id_param,
            transaction_date_param,
            refund_reason_param,
            status_param,
            user_id_param,
            sale_id_param
        ])