import datetime
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from base.models import Order, Customer, OrderLog, OrderLine
from .serializers import OrderSerializer, CustomerSerializer, OrderLogSerializer, OrderLineSerializer

class OrderAPI(APIView):
    # Get all orders or specific order
    def get(self, request, pk=None):
        if pk is not None:
            try:
                orders = Order.objects.get(id=pk)
                serialized_orders = OrderSerializer(orders)
                return Response(serialized_orders.data, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            orders = Order.objects.all()
            serialized_orders = OrderSerializer(orders, many=True)
            return Response(serialized_orders.data, status=status.HTTP_200_OK)
    
    # Generate random order
    def post(self, request):
        context = {}

        # Pick a random customer
        customers = Customer.objects.all()
        serialized_customers = CustomerSerializer(customers, many=True)
        randomCustomerID = random.randint(1,len(serialized_customers.data))
        
        # Generate Order
        order_data = {
            'customer': Customer.objects.get(id=randomCustomerID)
        }
        order = Order.objects.create(**order_data)
        serialized_order = OrderSerializer(order)
        context['order'] = serialized_order.data

        # Create log
        try:
            order_log_data = {
                'order': order,
                'time_stamp': datetime.datetime.now(),
                'incident': "Order created"
            }
            order_log = OrderLog.objects.create(**order_log_data)
            serialized_order_log = OrderLogSerializer(order_log)
            context['order_log'] = serialized_order_log.data
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate OrderLine(s)
        order_lines = []
        amount_of_order_lines = random.randint(1,3)
        iterator = 0
        while iterator < amount_of_order_lines:
            order_line_data = {
                'order': order,
                'item_number': random.randint(100,999),
                'amount': random.randint(1,10),
            }
            order_line = OrderLine.objects.create(**order_line_data)
            serialized_order_line = OrderLineSerializer(order_line)
            order_lines.append(serialized_order_line.data)
            iterator += 1
            # Create log
            try:
                order_log_data = {
                    'order': order,
                    'time_stamp': datetime.datetime.now(),
                    'incident': "OrderLine " + str(order_line.id) + " added to order"
                }
                order_log = OrderLog.objects.create(**order_log_data)
                serialized_order_log = OrderLogSerializer(order_log)
                context['order_log'] = serialized_order_log.data
            except Order.DoesNotExist:
                return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        context['order_lines'] = order_lines
        return Response(context, status=status.HTTP_201_CREATED)
    
    # Update order
    def patch (self, request, pk):
        context = {}
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        order.order_status = request.data.get('order_status', order.order_status)
        order.save()
        serialized_order = OrderSerializer(order)
        context['order'] = serialized_order.data

        # Create log
        try:
            order = Order.objects.get(id=pk)
            order_log_data = {
                'order': order,
                'time_stamp': datetime.datetime.now(),
                'incident': "Order status updated to " + str(order.order_status)
            }
            order_log = OrderLog.objects.create(**order_log_data)
            serialized_order_log = OrderLogSerializer(order_log)
            context['order_log'] = serialized_order_log.data
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(context, status=status.HTTP_200_OK)

    
    # Delete order
    def delete(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
            order.delete()
            return Response({"message": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

class OrderLineAPI(APIView):
    # Get all relevant order lines
    def get(self, request, order_id):
        order_lines = OrderLine.objects.filter(order__id=order_id)
        if order_lines.exists():
            serialized_order_lines = OrderLineSerializer(order_lines, many=True)
            return Response(serialized_order_lines.data, status=status.HTTP_200_OK)
        else:
            return Response([],status=status.HTTP_204_NO_CONTENT)
    
    # Update order line
    def patch(self, request, order_id, order_line_id):
        context = {}
        try:
            order_line = OrderLine.objects.get(pk=order_line_id)
        except OrderLine.DoesNotExist:
            return Response({"error": "Order line not found"}, status=status.HTTP_404_NOT_FOUND)
        order_line.order_line_status = request.data.get('order_line_status', order_line.order_line_status)
        order_line.save()
        serialized_order_line = OrderLineSerializer(order_line)
        context['order_line'] = serialized_order_line.data

        # Create log
        try:
            order = Order.objects.get(id=order_id)
            order_log_data = {
                'order': order,
                'time_stamp': datetime.datetime.now(),
                'incident': "Order line " + str(order_line_id) + " status updated to " + str(order_line.order_line_status)
            }
            order_log = OrderLog.objects.create(**order_log_data)
            serialized_order_log = OrderLogSerializer(order_log)
            context['order_log'] = serialized_order_log.data
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(context, status=status.HTTP_200_OK)
    
class OrderLogAPI(APIView):
    # Get all relevant order logs
    def get(self, request, order_id):
        order_logs = OrderLog.objects.filter(order__id=order_id)
        if order_logs.exists():
            serialized_order_logs = OrderLogSerializer(order_logs, many=True)
            return Response(serialized_order_logs.data, status=status.HTTP_200_OK)
        else:
            return Response([],status=status.HTTP_204_NO_CONTENT)
        
    # Create order log
    def post(self, request, order_id):
        incident = request.data.get("incident")
        context = {}
        try:
            order = Order.objects.get(id=order_id)
            serialized_order = OrderSerializer(order)
            context['order'] = serialized_order.data
            order_log_data = {
                'order': order,
                'time_stamp': datetime.datetime.now(),
                'incident': incident
            }
            order_log = OrderLog.objects.create(**order_log_data)
            serialized_order_log = OrderLogSerializer(order_log)
            context['order_log'] = serialized_order_log.data
            return Response(context, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)