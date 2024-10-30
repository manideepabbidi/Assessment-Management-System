# assessment/models.py

from django.db import models
import datetime
class Student(models.Model):
    id=models.CharField(max_length=100,unique=True,primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True)
    date_of_birth = models.DateField(default=datetime.date(2000, 1, 1))
    # Add more fields as needed

class Course(models.Model):
    name = models.CharField(max_length=100,unique=True,primary_key=True)
    description = models.TextField()
    # Add more fields as needed

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course= models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    # Add more fields as needed

class Assignment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Add more fields as needed

class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submission_date = models.DateTimeField(auto_now_add=True)
    # Add more fields as needed
