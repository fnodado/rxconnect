from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from inventory.forms import ProductForm, SupplierForm
from inventory.models import Product, Supplier


# Create your views here.
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

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
    supplier = get_object_or_404(Supplier, supplier_id=supplier_id)

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
    supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
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
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product-list')  # Redirect to the product list

@login_required
def edit_product(request, product_id):
    page = 'edit_product'
    print(product_id)
    product = get_object_or_404(Product, product_id=product_id)
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