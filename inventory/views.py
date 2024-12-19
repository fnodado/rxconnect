from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from inventory.forms import ProductForm, SupplierForm
from inventory.models import Product, Supplier
from django.db import connection, DatabaseError


# Create your views here.
@login_required
def product_list(request):
    try:
        #with statement in python is used for resource management.
        #It ensures ;actions like opening/closing are handled automatically
        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('rxconnect.get_all_products')
            products = cursor.fetchall()

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                product_list = [dict(zip(columns, row)) for row in products]

    except DatabaseError as e:
        # Log the error and return an empty list or error page
        print(f"Database error occurred: {e}")
        product_list = []

    print("product_list: ", product_list)

    # products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': product_list})

@login_required
def supplier_list(request):
    try:
        with connection.cursor() as cursor:
            # Call the stored supplier
            cursor.callproc('rxconnect.get_all_supplier')
            supplier = cursor.fetchall()

            if cursor.description:
                columns = [col[0] for col in cursor.description]
                supplier_list = [dict(zip(columns, row)) for row in supplier]

    except DatabaseError as e:
        # Log the error and return an empty list or error page
        print(f"Database error occurred: {e}")
        supplier_list = []

    print("supplier_list: ", supplier_list)
    # suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': supplier_list})

#Supplier vies CRUD
@login_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier-list')  # Redirect to supplier list after saving
    else:
        form = SupplierForm()
    return render(request, 'inventory/add_edit_supplier.html', {'form': form, 'page': 'add_supplier'})


@login_required
def edit_supplier(request, supplier_id):
    supplier = get_supplier_by_id(supplier_id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier-list')  # Redirect to supplier list after saving
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'inventory/add_edit_supplier.html',
                  {'form': form, 'page': 'edit_supplier', 'supplier': supplier})

@login_required
def delete_supplier(request, supplier_id):
    supplier = get_supplier_by_id(supplier_id)
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier-list')  # Redirect to the product list

# Product views CRUD
@login_required
def add_product(request):
    page = 'add_product'
    print(request.method)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product-list')  # Redirect to the product list
    else:
        form = ProductForm()
    context = {'page': page, 'form': form}
    return render(request, 'inventory/add_edit_product.html', context)

@login_required
def delete_product(request, product_id):
    # product = get_object_or_404(Product, product_id=product_id)
    product = get_product_by_id(product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product-list')  # Redirect to the product list

@login_required
def edit_product(request, product_id):
    page = 'edit_product'
    print(product_id)
    product = get_product_by_id(product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            print(f"Form is valid, saving product: {product_id}")
            form.save()
            return redirect('product-list')  # Redirect to the product list
        else:
            print(f"Form is not valid. Errors: {form.errors}")
    else:
        form = ProductForm(instance=product)
    context = {'page': page, 'form': form}
    return render(request, 'inventory/add_edit_product.html', {'form': form, 'product': product})


def get_product_by_id(product_id):
    try:
        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('rxconnect.get_product_by_id', [product_id])

            # Fetch one product
            row = cursor.fetchone()

            if not row:
                raise Http404("Product does not exist")

            # columns = [col[0] for col in cursor.description]
            # product = dict(zip(columns, row))
            product = Product(
                product_id=row[0],
                name=row[1],
                unit_price=row[2],
                current_stock=row[3],
                description=row[4]
            )

            return product

    except Exception as e:
        print(f"Error: {e}")
        raise Http404("Product does not exist")

def get_supplier_by_id(supplier_id):
    try:
        with connection.cursor() as cursor:
            # Call the stored procedure
            cursor.callproc('rxconnect.get_supplier_by_id', [supplier_id])

            # Fetch one product
            row = cursor.fetchone()

            if not row:
                raise Http404("Supplier does not exist")

            # columns = [col[0] for col in cursor.description]
            # product = dict(zip(columns, row))
            supplier = Supplier(
                supplier_id=row[0],
                name=row[1],
                contact_info=row[2],
            )

            return supplier

    except Exception as e:
        print(f"Error: {e}")
        raise Http404("Supplier does not exist")