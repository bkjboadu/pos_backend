from django.contrib import admin
from .models import OrderItem, Order,Shipment

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Shipment)
