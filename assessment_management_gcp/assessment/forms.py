from django import forms
from .models import Student, Course, Assignment, Submission

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'date_of_birth']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['name', 'description', 'due_date', 'course']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['student', 'assignment', 'file']
