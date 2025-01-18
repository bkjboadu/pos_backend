from payment.models import Payment
from inventory_management.models import Product
from sales.models import Transaction, TransactionItem
from discounts.models import Promotion, Discount
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os



def create_transaction(items, total_amount=None, customer=None):
    # create transaction
    try:
        with transaction.atomic():
            print(customer)
            if total_amount is not None:
                transaction_instance = Transaction.objects.create(
                    total_amount=total_amount,
                    customer=customer
                )
            else:
                transaction_instance = Transaction.objects.create(
                    customer=customer
                )

            for item in items:
                # get product instance
                product = get_object_or_404(Product, id=item["product"])
                TransactionItem.objects.create(
                    transaction=transaction_instance,
                    product=product,
                    quantity=item["quantity"],
                    total_amount=item["quantity"] * product.price,
                )
            transaction_instance.save()
        return transaction_instance
    except Exception as e:
        raise ValueError(e)


def get_total_amount(items):
    try:
        total_amount = 0
        for item in items:
            product = get_object_or_404(Product, id=item["product"])
            total_amount += item["quantity"] * product.price
        return total_amount
    except Exception as e:
        raise ValueError(e)


def activate_discount(discount_code, total_amount):
    try:
        discount = get_object_or_404(Discount, code=discount_code, is_active=True)
        if discount.discount_type == "percentage":
            total_amount *= 1 - (discount.value / 100)
            print(total_amount)
        elif discount.discount_type == "fixed":
            total_amount = max(0, total_amount - discount.value)
            print(total_amount)
        return total_amount
    except Exception:
        return Response({"message": "Invalid or expired discount code"}, status=400)


def activate_promotion(name, total_amount):
    try:
        promotion = get_object_or_404(Promotion, code=name, is_active=True)
        if promotion.discount.discount_type == "percentage":
            total_amount *= 1 - (promotion.discount.value / 100)
        elif promotion.discount.discount_type == "fixed":
            total_amount = max(0, total_amount - promotion.disount.value)
        return total_amount
    except Exception:
        return Response({"message": "Invalid or expired discount code"}, status=400)

def generate_receipt_data(transaction):
    """
    Generate receipt data from a Transaction instance.

    Args:
        transaction (Transaction): The transaction instance.

    Returns:
        dict: A dictionary containing receipt data.
    """
    # Retrieve customer information
    customer = transaction.customer
    customer_data = {
        "name": f"{customer.first_name} {customer.last_name}" if customer else "Guest",
        "phone": customer.phone_number if customer else "N/A",
    }

    # Retrieve transaction items
    items = [
        {
            "name": item.product.name,
            "quantity": item.quantity,
            "price": float(item.product.price),
        }
        for item in transaction.items.all()
    ]

    # Compile receipt data
    receipt_data = {
        "receipt_id": f"TRANS-{transaction.id}",
        "customer": customer_data,
        "items": items,
        "cashier": transaction.created_by.first_name if transaction.created_by else "Unknown",
    }

    return receipt_data

class ReceiptGenerator:
    def __init__(self, receipt_folder="receipts"):
        self.receipt_folder = receipt_folder
        os.makedirs(receipt_folder, exist_ok=True)


    def generate_small_receipt(self, receipt_data):
        """
        Generates a small-sized receipt.

        Args:
            receipt_data (dict): Information to include in the receipt.
        """
        # Define the small receipt size: 3.15 inches (80mm) by custom length
        receipt_width = 3.15 * 72  # Convert inches to points
        receipt_height = 10 * 72   # Start with a tall receipt to dynamically adjust
        file_name = f"{self.receipt_folder}/receipt_{receipt_data['receipt_id']}.pdf"
        c = canvas.Canvas(file_name, pagesize=(receipt_width, receipt_height))

        # Set the starting position for the text
        y = receipt_height - 20

        # Add Header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y, "POS Receipt")
        y -= 15

        c.setFont("Helvetica", 8)
        c.drawString(10, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(120, y, f"Receipt ID: {receipt_data['receipt_id']}")
        y -= 20

        # Add Cashier Info
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, y, "Cashier:")
        c.setFont("Helvetica", 8)
        c.drawString(60, y, receipt_data['cashier'])
        y -= 15

        # Add Customer Info
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, y, "Customer:")
        c.setFont("Helvetica", 8)
        customer = receipt_data["customer"]
        c.drawString(60, y, f"{customer['name']} ({customer['phone']})")
        y -= 20

        # Add Items Table
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, y, "Items:")
        y -= 15
        c.setFont("Helvetica", 8)
        c.drawString(10, y, "Name")
        c.drawString(100, y, "Qty")
        c.drawString(140, y, "Price")
        c.drawString(180, y, "Total")
        y -= 15

        total_amount = 0
        for item in receipt_data["items"]:
            c.drawString(10, y, item["name"])
            c.drawString(100, y, str(item["quantity"]))
            c.drawString(140, y, f"${item['price']:.2f}")
            item_total = item["quantity"] * item["price"]
            c.drawString(180, y, f"${item_total:.2f}")
            total_amount += item_total
            y -= 15

        # Add Total Amount
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10, y, f"Total Amount: ${total_amount:.2f}")
        y -= 20

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(10, y, "Thank you for shopping with us!")

        c.showPage()
        c.save()
        print(f"Receipt saved as {file_name}")
        return file_name

    def generate_receipt(self, receipt_data):
        """
        Generates a PDF receipt.

        Args:
            receipt_data (dict): Information to include in the receipt.
        """
        receipt_id = receipt_data["receipt_id"]
        file_name = f"{self.receipt_folder}/receipt_{receipt_id}.pdf"
        c = canvas.Canvas(file_name, pagesize=letter)

        # Add Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "POS Receipt")

        c.setFont("Helvetica", 10)
        c.drawString(100, 735, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(400, 735, f"Receipt ID: {receipt_id}")

        # Add Cashier Info
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 710, "Cashier Information:")
        c.setFont("Helvetica", 10)
        c.drawString(100, 695, f"Cashier: {receipt_data['cashier']}")

        # Add Customer Info
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 675, "Customer Information:")
        c.setFont("Helvetica", 10)
        customer = receipt_data["customer"]
        c.drawString(100, 660, f"Name: {customer['name']}")
        c.drawString(100, 645, f"Phone: {customer['phone']}")

        # Add Items Table
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 620, "Items Purchased:")
        c.setFont("Helvetica", 10)
        y = 605
        c.drawString(100, y, "Item")
        c.drawString(300, y, "Qty")
        c.drawString(350, y, "Price")
        c.drawString(400, y, "Total")
        y -= 15

        total_amount = 0
        for item in receipt_data["items"]:
            c.drawString(100, y, item["name"])
            c.drawString(300, y, str(item["quantity"]))
            c.drawString(350, y, f"${item['price']:.2f}")
            item_total = item["quantity"] * item["price"]
            c.drawString(400, y, f"${item_total:.2f}")
            total_amount += item_total
            y -= 15

        # Add Total Amount
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y - 10, f"Total Amount: ${total_amount:.2f}")

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(100, 50, "Thank you for shopping with us!")

        c.save()
        print(f"Receipt saved as {file_name}")
        return file_name
