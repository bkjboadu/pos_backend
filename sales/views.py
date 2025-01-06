from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from inventory_management.models import Product
from .models import Transaction, TransactionItem
from .serializer import TransactionSerializer, TransactionItemSerializer


class TransactionView(APIView):
    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

class TransactionDetailView(APIView):
    def get(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)
        transaction.delete()
        return Response({"message":"Transaction deleted successfully"}, status=200)


    def put(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        transaction = Transaction.objects.get(pk=pk)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)



class TransactionItemView(APIView):
    def get(self, request):
        transaction_items = TransactionItem.objects.all()
        serializer = TransactionItemSerializer(transaction_items, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = TransactionItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

class TransactionItemDetailView(APIView):
    def get(self, request, pk):
        transaction_item = TransactionItem.objects.get(pk=pk)
        serializer = TransactionItemSerializer(transaction_item)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        transaction_item = TransactionItem.objects.get(pk=pk)
        transaction_item.delete()
        return Response({"message":"Transaction Item deleted successfully"}, status=200)


    def put(self, request, pk):
        transaction_item = TransactionItem.objects.get(pk=pk)
        serializer = TransactionItemSerializer(transaction_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        transaction_item = TransactionItem.objects.get(pk=pk)
        serializer = TransactionItemSerializer(transaction_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
