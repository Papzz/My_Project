from django.urls import path, include
from . import views
from . import templates
from .views import EmployeeDetailView, ServiceDetailView, ServiceDetailView, service_delete, save_service, service_base, \
    print_service, service_employee_detail, simple_mail, logout, service_employee, change_status, get_darbinieki, \
    drive_print
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import make_password

urlpatterns = [
    path("employee_base", views.employee_base, name="employee_base"),
    path("employee", views.employee, name='employee'),
    path('employee/<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('employee/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employee/<int:pk>/save/', views.save_employee, name='save_employee'),
    path('service_base', views.service_base, name='service_base'),
    path("service", views.service, name='service'),
    path('service_base/<str:status>/', service_base, name='service_base_status'),
    path('service_employee/', views.service_employee, name='service_employee'),
    path('service_employee/<str:status>/', views.service_employee, name='service_employee_status'),
    path('service/<int:pk>/', ServiceDetailView.as_view(), name='service_detail'),
    path('service/<int:pk>/delete/', service_delete, name='service_delete'),
    path('service/<int:pk>/save/', save_service, name='save_service'),
    path('prof_base', views.prof_base, name="prof_base"),
    path('prof/<int:pk>/delete', views.prof_delete, name='prof_delete'),
    path('prof_edit/<int:pk>/', views.prof_edit, name='prof_edit'),
    path('login/', views.login_view, name='login'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_service/', views.user_service, name='user_service'),
    path('infosave/<int:pk>/', views.infosave, name='infosave'),
    path('print_service/<int:pk>/', print_service, name='print_service'),
    path('drive_print/<int:pk>/', drive_print, name='drive_print'),
    path('service_employee_detail/<int:pk>/', service_employee_detail, name='service_employee_detail'),
    path('mail', simple_mail),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', logout, name='logout'),
    path('save_service', views.save_service, name='save_service'),
    path('save_darb_apraksts/<int:pk>/', views.save_darb_apraksts, name='save_darb_apraksts'),
    path('change_status/', change_status, name='change_status'),
    path('change_password/', views.change_password, name='change_password'),
    path('get_darbinieki', get_darbinieki, name='get_darbinieki'),
    path('save_darb_apraksts/<int:pk>/', views.save_darb_apraksts, name='save_darb_apraksts'),
    path('save_completed/<int:pk>/', views.save_completed, name='save_completed'),
    path('izbraukums', views.izbraukums, name='izbraukums'),
]
