from django.forms import ModelForm
from django import forms
from .models import Student, Teacher

class StudentForm(ModelForm):
    class Meta:
        model = Student
        exclude = ['id', 'classrooms', 'courses']


class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ['hire_date', 'education_degree']


class TeacherSearchForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False, label='نام')
    last_name = forms.CharField(max_length=20, required=False, label='نام خانوادگی')
    from_hire_date = forms.DateField(required=False, label='از تاریخ')
    to_hire_date = forms.DateField(required=False, label='تا تاریخ')
    education_degree = forms.CharField(max_length=20, required=False, label='مدرک تحصیلی')


class StudentSearchForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False, label='نام')
    last_name = forms.CharField(max_length=20, required=False, label='نام خانوادگی')

