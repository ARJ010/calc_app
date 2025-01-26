from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_user, name='register_user'),
    path('advocate_list/',views.advocate_list, name='advocate_list'),
    path('advocate_details/<int:advocate_id>/',views.advocate_list, name='advocate_details'),
    path('advocates/bulk_register/', views.bulk_register_advocates, name='bulk_register_advocates'),
]