from django.urls import path
from . import views

urlpatterns = [
    #product urls
    path('products/', views.product_list, name="product-list"),
    path('products/add/', views.add_product, name='add-product'),
    path('products/<str:product_id>/edit/', views.edit_product, name='edit-product'),
    path('products/<str:product_id>/delete/', views.delete_product, name='delete-product'),

    #supplier urls
    path('suppliers/', views.supplier_list, name="supplier-list"),
    path('suppliers/add/', views.add_supplier, name='add-supplier'),
    path('suppliers/<str:supplier_id>/edit/', views.edit_supplier, name='edit-supplier'),
    path('suppliers/<str:supplier_id>/delete/', views.delete_supplier, name='delete-supplier'),
]