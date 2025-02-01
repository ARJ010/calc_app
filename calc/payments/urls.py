from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_advocate, name='register_advocate'),
    path('advocate_list/',views.advocate_list, name='advocate_list'),
    path('advocate_details/<int:advocate_id>/',views.advocate_detail, name='advocate_details'),
    path('upload/', views.upload_advocates, name='bulk_add_advocates'),
    path('export/advocates/', views.export_advocates_csv, name='export_advocates_csv'),
    path('edit_profile/<int:advocate_id>/', views.edit_advocate, name='edit_advocate'),
    path('download/', views.download_advocate_template, name='download_advocate_template'),
    path('advocate/make_payment/<int:advocate_id>/', views.make_payment, name='make_payment'),
]   