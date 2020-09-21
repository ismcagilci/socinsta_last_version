from django.urls import path

from . import views

app_name="payment"

urlpatterns = [
    path('card/',views.add_cart,name='card'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
    path('remove_item/',views.remove_item,name='remove_item'),
    path('callback/',views.callback,name='callback'),
    path('create_package/', views.create_packages,name='create_package'),
    path('havale/',views.havale,name ="havale"),
]