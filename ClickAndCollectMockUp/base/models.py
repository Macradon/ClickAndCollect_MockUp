from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=200, default="Created")

class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_number = models.CharField(max_length=200)
    amount = models.IntegerField()
    order_line_status = models.CharField(max_length=200, default="Not-ready")

class OrderLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField()
    incident = models.CharField(max_length=200, default='redacted')