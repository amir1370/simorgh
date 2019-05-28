from django.forms import ModelForm
from django import forms
from .models import Student, Teacher, Classroom, TeacherClassCourse, Register, User, ClassTime, Course
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q


class DateInput(forms.DateInput):
    input_type = 'date'


class StudentForm(ModelForm):
    student_id = forms.IntegerField(label='شماره دانش آموزی')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_active']


class TeacherForm(ModelForm):
    username = forms.CharField(max_length=120, label='نام کاربری')
    first_name = forms.CharField(max_length=150, label='نام')
    last_name = forms.CharField(max_length=150, label='نام خانوادگی')
    is_active = forms.BooleanField(label='فعال')

    # user_id = forms.IntegerField(required=False)
    class Meta:
        model = Teacher
        exclude = ['user']
        widgets = {
            'hire_date': DateInput(),
        }


class TeacherSearchForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False, label='نام')
    last_name = forms.CharField(max_length=20, required=False, label='نام خانوادگی')
    from_hire_date = forms.DateField(required=False, label='از تاریخ')
    to_hire_date = forms.DateField(required=False, label='تا تاریخ')
    DIPLOMA, ASSOCIATE, BACHELOR, MASTER, PHD, EMPTY = 'DP', 'AS', 'BA', 'MA', 'PHD', None
    degree_choices = (
        (EMPTY, '-----'),
        (DIPLOMA, 'دیپلم'),
        (ASSOCIATE, 'فوق دیپلم'),
        (BACHELOR, 'لیسانس'),
        (MASTER, 'فوق لیسانس'),
        (PHD, 'دکتری')
    )
    education_degree = forms.ChoiceField(choices=degree_choices, initial='', required=False, label='مدرک تحصیلی')

    def __init__(self, *args, **kwargs):
        super(TeacherSearchForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control mb-3'


class StudentSearchForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False, label='نام')
    last_name = forms.CharField(max_length=20, required=False, label='نام خانوادگی')

    def __init__(self, *args, **kwargs):
        super(StudentSearchForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control mb-3'


class ClassroomForm(ModelForm):
    class Meta:
        model = Classroom
        exclude = ['courses', 'teachers']


class ClassroomSearchForm(forms.Form):
    FIRST, SECOND, THIRD, EMPTY = 'first', 'second', 'third', None
    level_choices = (
        (EMPTY, '-----'),
        (FIRST, 'اول'),
        (SECOND, 'دوم'),
        (THIRD, 'سوم')
    )
    level = forms.ChoiceField(choices=level_choices, required=False, label='پایه')
    MATH, NATURAL, HUMANITY, EMPTY = 'math', 'natural', 'humanity', None
    field_choices = (
        (EMPTY, '-----'),
        (MATH, 'ریاضی'),
        (NATURAL, 'تجربی'),
        (HUMANITY, 'انسانی')
    )
    field = forms.ChoiceField(choices=field_choices, required=False, label='رشته')
    A, B, C, EMPTY = 'a', 'b', 'c', None
    branch_choices = (
        (EMPTY, '-----'),
        (A, 'الف'),
        (B, 'ب'),
        (C, 'ج')
    )
    branch = forms.ChoiceField(choices=branch_choices, required=False, label='گروه')
    education_year = forms.CharField(max_length=20, required=False, label='سال تحصیلی')

    def __init__(self, *args, **kwargs):
        super(ClassroomSearchForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control mb-3'


class TeacherClassCourseForm(ModelForm):
    class Meta:
        model = TeacherClassCourse
        exclude = ['classroom']

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super().__init__(*args, **kwargs)
        classroom = Classroom.objects.get(id=pk)
        object_list = []
        for my_object in list(TeacherClassCourse.objects.filter(classroom=classroom)):
            object_list.append(my_object)
        self.fields['class_time'].queryset = ClassTime.objects.filter(~Q(teacher_class_course__in=object_list))
        self.fields['course'].queryset = Course.objects.filter(~Q(teacher_class_courses__in=object_list))

class RegisterForm(ModelForm):
    class Meta:
        model = Register
        fields = '__all__'


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'
