from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register_advocate, name='register_advocate'),
    path('advocate_list/',views.advocate_list, name='advocate_list'),
    path('advocate_details/<int:advocate_id>/',views.advocate_detail, name='advocate_details'),
    path('upload/', views.upload_advocates, name='bulk_add_advocates'),
    path('export/advocates/', views.export_advocates_csv, name='export_advocates_csv'),
    path('edit_profile/<int:advocate_id>/', views.edit_advocate, name='edit_advocate'),
    path('download/', views.download_advocate_template, name='download_advocate_template'),
    path('check-dues/', views.check_and_update_dues, name='check_dues'),
    path('advocate/<int:advocate_id>/debt-pay/', views.debt_pay, name='debt_pay'),
    path('advocate/<int:advocate_id>/normal-pay/', views.normal_pay, name='normal_pay'),
    path('manage-admins/', views.manage_admins, name='manage_admins'),
    path('edit-admin/', views.edit_admin, name='edit_admin'),
    path('change-username-password/', views.change_username_password, name='change_username_password'),
    path('reset_advocate_credentials/<str:advocate_id>/', views.reset_advocate_credentials, name='reset_advocate_credentials'),
    path('report/', views.payment_due_report, name='payment_due_report'),
    path('delete_advocate/<int:advocate_id>/', views.delete_advocate, name='delete_advocate'),
    path('certificate/<int:advocate_id>/', views.generate_experience_certificate, name='generate_certificate'),

]   