from django.urls import path
from . import views
from instagram.tasks import *

app_name="instagram"

urlpatterns = [
    path('select_assistant/',views.select_assistant),
    path('create_assistant',views.create_assistant),
    path('add_insta_account',views.add_insta_account),
    path('delete_ig_account',views.delete_ig_account),
    path('delete_ig_account_navbar/<str:user>',views.delete_ig_account_navbar),
    path('change_active_account/<str:username>',views.change_active_account),
    path('assistants_details/',views.assistants_details),
    path('profile/',views.profile),
    path('dashboard/',views.dashboard),
    path('',views.dashboard),

]