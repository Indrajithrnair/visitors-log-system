from django.urls import path
from . import views

urlpatterns = [
    # Report URLs
    path('report/', views.report_visitor, name='report_visitor'),
    path('report/<int:visit_id>/', views.report_visitor, name='report_specific_visitor'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    
    # Blacklist URLs
    path('blacklist/', views.blacklist_list, name='blacklist_list'),
    path('blacklist/create/', views.create_blacklist, name='create_blacklist'),
    path('blacklist/create/<int:report_id>/', views.create_blacklist, name='create_blacklist'),
    path('blacklist/<int:pk>/', views.blacklist_detail, name='blacklist_detail'),
    path('blacklist/<int:pk>/edit/', views.edit_blacklist, name='edit_blacklist'),
    path('blacklist/<int:pk>/delete/', views.delete_from_blacklist, name='delete_from_blacklist'),
] 