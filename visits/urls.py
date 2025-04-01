from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_visit_request, name='create_visit_request'),
    path('list/', views.visit_list, name='visit_list'),
    path('resident/', views.resident_visit_requests, name='resident_visit_requests'),
    path('approve-reject/<int:pk>/', views.approve_reject_visit, name='approve_reject_visit'),
    path('detail/<int:pk>/', views.visit_detail, name='visit_detail'),
    path('check-in/<int:pk>/', views.check_in_visit, name='check_in_visit'),
    path('check-out/<int:pk>/', views.check_out_visit, name='check_out_visit'),
] 