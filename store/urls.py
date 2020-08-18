from django.contrib import admin
from django.urls import path, include
from . import views

app_name='store'
urlpatterns = [
    path('',views.store, name='store' ),
    path('cart/',views.cart, name='cart'),
    path('checkout/',views.checkout, name='checkout'),
    path('update_item/',views.updateItem, name='updateItem'),
    path('process_order/',views.processOrder, name='processOrder'),
    path('payment_form/<str:pk>/',views.payment, name='payment'),
    path('login/',views.login, name='login'),
    path('register/',views.register, name='register'),
    path('logout/',views.logout, name='logout'),
    path('product/<str:pk>', views.product, name='product'),
    path('delete/<str:pk>/<str:pk2>', views.delete, name='delete'),
    path('rate/<str:pk>',views.rate, name='rate'),
]
