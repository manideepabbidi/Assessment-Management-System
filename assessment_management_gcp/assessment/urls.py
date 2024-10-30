# assessment/urls.py

from django.urls import path
from . import views

urlpatterns = [
        path('', views.home, name='home'),

    path('students/', views.student_list, name='student_list'),
    path('add-student/', views.add_student, name='add_student'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.file_list, name='file_list'),
    path('file/<str:file_name>/', views.download_file, name='download_file'),
    path('delete/<str:file_name>/', views.delete_file, name='delete_file'),
    path('train/', views.train_model, name='train_model'),
    path('process/', views.process_firestore_document, name='process_firestore_document'),
    path('analyze/', views.analyze_and_export_to_bigquery, name='analyze'),
]