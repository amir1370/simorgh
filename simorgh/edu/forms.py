from django.forms import ModelForm
from django import forms
from .models import Student

class StudentForm(ModelForm):
    class Meta:
        model = Student
        exclude = ['id', 'classrooms', 'courses']


class TeacherSearchForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    from_hire_date = forms.DateField(required=False)
    to_hire_date = forms.DateField(required=False)
    education_degree = forms.CharField(max_length=20, required=False)