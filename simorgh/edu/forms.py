from django.forms import ModelForm
from django import forms
from .models import Student, Teacher, Classroom, TeacherClassCourse, Register

class StudentForm(ModelForm):
    class Meta:
        model = Student
        exclude = ['id', 'classrooms', 'courses', 'last_modified_date']


class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = '__all__'


class TeacherSearchForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False, label='نام')
    last_name = forms.CharField(max_length=20, required=False, label='نام خانوادگی')
    from_hire_date = forms.DateField(required=False, label='از تاریخ')
    to_hire_date = forms.DateField(required=False, label='تا تاریخ')
    DIPLOMA, ASSOCIATE, BACHELOR, MASTER, PHD, EMPTY = 'DP', 'AS', 'BA', 'MA', 'PHD', None
    degree_choices = (
        (EMPTY, 'همه موارد'),
        (DIPLOMA, 'دیپلم'),
        (ASSOCIATE, 'فوق دیپلم'),
        (BACHELOR, 'لیسانس'),
        (MASTER, 'فوق لیسانس'),
        (PHD, 'دکتری')
    )
    education_degree = forms.ChoiceField(choices=degree_choices, initial='', required=False, label='مدرک تحصیلی')


class StudentSearchForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False, label='نام')
    last_name = forms.CharField(max_length=20, required=False, label='نام خانوادگی')


class ClassroomForm(ModelForm):
    class Meta:
        model = Classroom
        exclude = ['courses', 'teachers']


class ClassroomSearchForm(forms.Form):
    FIRST, SECOND, THIRD, EMPTY = 'first', 'second', 'third', None
    level_choices = (
        (EMPTY, 'همه موارد'),
        (FIRST, 'اول'),
        (SECOND, 'دوم'),
        (THIRD, 'سوم')
    )
    level = forms.ChoiceField(choices=level_choices, required=False, label='پایه')
    MATH, NATURAL, HUMANITY, EMPTY = 'math', 'natural', 'humanity', None
    field_choices = (
        (EMPTY, 'همه موارد'),
        (MATH, 'ریاضی'),
        (NATURAL, 'تجربی'),
        (HUMANITY, 'انسانی')
    )
    field = forms.ChoiceField(choices=field_choices, required=False, label='رشته')
    A, B, C, EMPTY = 'a', 'b', 'c', None
    branch_choices = (
        (EMPTY, 'همه موارد'),
        (A, 'الف'),
        (B, 'ب'),
        (C, 'ج')
    )
    branch = forms.ChoiceField(choices=branch_choices, required=False, label='گروه')
    education_year = forms.CharField(max_length=20, required=False, label='سال تحصیلی')


class TeacherClassCourseForm(ModelForm):
    class Meta:
        model = TeacherClassCourse
        fields = '__all__'


class RegisterForm(ModelForm):
    class Meta:
        model = Register
        fields = '__all__'