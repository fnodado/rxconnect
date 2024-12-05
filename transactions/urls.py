from django.urls import path
from . import views

urlpatterns = [
    #purchase transaction urls
    path('purchase/', views.purchase_list, name="purchase-list"),
    path('purchase/add/', views.purchase_transaction, name='add-purchase'),

    #sale transaction urls
    path('sale/', views.sale_transaction, name='sale-transaction'),
    path('sale/list', views.sale_list, name="sales-list"),
    path('sale-item/<int:sale_id>/', views.sale_item, name='sale-item'),
    path('checkout-item/<int:sale_id>/', views.checkout, name='checkout-item'),
    path('complete/<int:sale_id>/', views.complete_sale, name='complete-sale'),
    path('delete-item/<int:item_id>/', views.delete_sale_item, name='delete-sale-item'),


]