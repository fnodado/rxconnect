from django.urls import path
from . import views

urlpatterns = [
    #purchase transaction urls
    path('purchase/', views.purchase_list, name="purchase-list"),
    path('purchase/add/', views.purchase_transaction, name='add-purchase'),
]