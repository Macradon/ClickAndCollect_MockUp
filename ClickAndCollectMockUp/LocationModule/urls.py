from django.urls import path
from . import views

urlpatterns = [
    path('show_orders/', views.show_orders, name='show_orders'),
    path('show_order/', views.show_order, name='show_order'),
]