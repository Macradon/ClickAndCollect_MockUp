from rest_framework import serializers
from base.models import Customer, Order, OrderLine, OrderLog

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'order_status']

class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ['id', 'order', 'item_number', 'amount', 'order_line_status']

class OrderLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLog
        fields = ['id', 'order', 'time_stamp', 'incident']