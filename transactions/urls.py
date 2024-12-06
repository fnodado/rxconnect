from django.urls import path
from . import views

from decimal import Decimal
from django.urls import register_converter

class DecimalConverter:
    regex = r'\\d+(\\.\\d+)?'

    def to_python(self, value):
        return Decimal(value)

    def to_url(self, value):
        return str(value)


register_converter(DecimalConverter, 'decimal')


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
    path('sale/<int:sale_id>/items/<int:return_id>', views.view_sale_items, name='view-sale-items'),

    #return transaction urls
    path('return/<int:sale_id>/', views.return_transaction, name='return-transaction'),
    path('return/checkout-item/<int:return_id>/', views.return_checkout, name='return-checkout-item'),
    path('return-item/<int:return_id>/<int:sale_item_id>', views.return_item, name='return-item'),
    path('return/delete/<int:return_item_id>/', views.delete_return_item, name='delete-return-item'),
    path('return/complete/<int:return_id>/', views.complete_return, name='complete-return'),
]