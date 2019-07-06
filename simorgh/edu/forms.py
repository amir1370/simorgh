import jdatetime
from django.forms import ModelForm, formset_factory
from django import forms
from .models import Student, Teacher, Classroom, TeacherClassCourse, Register, User, ClassTime, Course, Assignment, \
    StudentPresence, TeacherPresence
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q
from directmessages.models import Message
from django.contrib.auth.models import Group


class DateInput(forms.DateInput):
    input_type = 'date'


class StudentForm(ModelForm):
    student_id = forms.IntegerField(label='شماره دانش آموزی')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'is_active']


class StudentUpdateForm(ModelForm):
    username = forms.CharField(max_length=120, label='نام کاربری')
    first_name = forms.CharField(max_length=150, label='نام')
    last_name = forms.CharField(max_length=150, label='نام خانوادگی')
    is_active = forms.BooleanField(label='فعال')

    class Meta:
        model = Student
        fields = ['student_id']

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super().__init__(*args, **kwargs)
        student = Student.objects.get(id=pk)
        self.fields['username'].initial = student.user.username
        self.fields['first_name'].initial = student.user.first_name
        self.fields['last_name'].initial = student.user.last_name
        self.fields['is_active'].initial = student.user.is_active



class TeacherForm(ModelForm):
    username = forms.CharField(max_length=120, label='نام کاربری')
    first_name = forms.CharField(max_length=150, label='نام')
    last_name = forms.CharField(max_length=150, label='نام خانوادگی')
    is_active = forms.BooleanField(label='فعال')
    hire_date = forms.CharField(max_length=150, label='تاریخ استخدام')

    # user_id = forms.IntegerField(required=False)
    class Meta:
        model = Teacher
        exclude = ['user']

    def clean_hire_date(self):
        hire_date = self.cleaned_data.get('hire_date')
        print(hire_date)
        (y, m, d) = hire_date.split('/')
        hire_date = jdatetime.date(year=int(y), month=int(m), day=int(d))
        print(hire_date)
        hire_date = jdatetime.date.togregorian(hire_date)
        print(hire_date)
        return hire_date


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
    MATH, NATURAL, HUMANITY, EMPTY = 'math', 'natural', 'humanity', None
    field_choices = (
        (EMPTY, '-----'),
        (MATH, 'ریاضی'),
        (NATURAL, 'تجربی'),
        (HUMANITY, 'انسانی')
    )
    field = forms.ChoiceField(choices=field_choices, initial='', required=False, label='رشته')

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
        fields = ['username', 'password', 'email']


class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(), label='ارسال به', widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Message
        fields = ['content']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = request.user
        if Group.objects.get(name='teacher') in user.groups.all():
            self.fields['recipients'].queryset = User.objects.filter(
                student__registers__is_active=True, student__classrooms__teachers=Teacher.objects.get(user=user)
            )
        elif Group.objects.get(name='manager') in user.groups.all():
            self.fields['recipients'].queryset = User.objects.all()


class AssignmentForm(ModelForm):
    class Meta:
        model = Assignment
        exclude = ['sent_time', 'grade']
        widgets = {
            'deadline_time': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if Group.objects.get(name='teacher') in user.groups.all():
            self.fields['teacher_class_course'].queryset = TeacherClassCourse.objects.filter(teacher__user=user)


class PlanningForm(forms.Form):
    teacher = forms.ModelChoiceField(queryset=Teacher.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    time_number = forms.IntegerField(max_value=4, min_value=1)
    Saturday, Sunday, Monday, Tuesday, Wednesday = 0, 1, 2, 3, 4
    day_choices = (
        (Saturday, 'شنبه'),
        (Sunday, 'یکشنبه'),
        (Monday, 'دوشنبه'),
        (Tuesday, 'سه شنبه'),
        (Wednesday, 'چهارشنبه')
    )
    days = forms.MultipleChoiceField(choices=day_choices, widget=forms.CheckboxSelectMultiple)


class StudentPresenceForm(forms.ModelForm):
    class Meta:
        model = StudentPresence
        fields = ['presence', 'activity']


StudentPresenceFormset = formset_factory(StudentPresenceForm)


class TeacherPresenceForm(forms.ModelForm):
    class Meta:
        model = TeacherPresence
        fields = ['presence']


TeacherPresenceFormset = formset_factory(TeacherPresenceForm)


class ClassTimeForm(forms.ModelForm):
    class Meta:
        model = ClassTime
        fields = ['day']