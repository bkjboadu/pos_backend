from django.contrib import admin
from .models import OrderItem, Order,Shipment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "name",
        "email",
        "phone_number",
        "order_number",
        "status",
        "payment_status",
        "total_amount"
        "created_at",
        "updated_at",
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "order",
        "product",
        "quantity",
        "price_at_order",
        "total_price"
    )



@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        "order",
        'tracking_number',
        'carrier',
        'status',
        'estimated_delivery',
        'shipped_at',
        'delivered_at'
    )
