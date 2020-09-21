from django.contrib import admin
from django.urls import path
from aristo import views

app_name="aristo"

urlpatterns = [
    #Standart pages
    path('landing/',views.landing),
    path('about/',views.landing),
    path('contact/',views.contact),
    path('pricing/',views.pricing),
    path('sozlesme/',views.sozlesme),

    #Auth Pages
    path('login/',views.login_user),
    path('register/',views.register),
    path('logout/',views.logout_user),
    path('forget_password/',views.forget_password),
    path('change_password/',views.change_password),

    #aq urls
    path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path(r'^change_password_confirmation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    views.change_password_confirmation, name='change_password_confirmation'),
]


