from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from assessment.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('create-student/', create_student, name='create_student'),
    path('create-course/', create_course, name='create_course'),
    path('create-assignment/', create_assignment, name='create_assignment'),
    path('submit-assignment/', submit_assignment, name='submit_assignment'),
    path('train/', train_model, name='train_model'),
    path('analyze/', analyze_and_export_to_bigquery, name='analyze'),
]