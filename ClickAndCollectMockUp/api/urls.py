from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.OrderAPI.as_view(), name='order_list'),
    path('order/<int:pk>/', views.OrderAPI.as_view(), name='order_details'),
    path('order/<int:order_id>/orderlines/', views.OrderLineAPI.as_view(), name='orderlines_list'),
    path('order/<int:order_id>/orderlines/<int:order_line_id>', views.OrderLineAPI.as_view(), name='orderline_details'),
    path('order/<int:order_id>/orderlogs/', views.OrderLogAPI.as_view(), name='orderlog_list'),
]