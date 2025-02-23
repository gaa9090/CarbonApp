from django.urls import path 
from .views import all_tracker, delete_tracker, analyse_csv, add_report, upload_file, all_report, view_report, delete_report, render_pdf_view

app_name = "tracker"


urlpatterns = [
    path('', all_tracker , name='tracker'),
    path('delete-tracker/<int:pk>/', delete_tracker, name='delete-tracker'),
    path('analyse/<int:pk>/', analyse_csv, name='analyse'),
    path('edit-tracker<int:pk>/', upload_file, name='upload'),
    path('add-report<int:pk>/', add_report, name='add-report'),

    # Reports
    # path('<slug:slug>delete-report<int:pk>/',views.delete_budget, name='delete-report'),
    # path('<slug:slug>report-detail<int:pk>/',views.view_report, name='view-report'),
    
    
    path('all-report/',all_report, name='all-report'),
    path('report-detail<int:pk>/',view_report, name='view-report'),
    path('delete-report<int:pk>/',delete_report, name='delete-report'),
    
    # Url Pdf
    path('pdf_report<int:pk>/',render_pdf_view, name='pdf-report'),

]







