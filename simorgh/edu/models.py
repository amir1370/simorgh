from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator


class Student(models.Model):
    student_id = models.IntegerField(verbose_name='شماره دانش آموزی')
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    courses = models.ManyToManyField('Course', through='StudentCourse', related_name='students')
    classrooms = models.ManyToManyField('Classroom', through='Register', related_name='students')
    last_modified_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    hire_date = models.DateField(null=True, blank=True, verbose_name='تاریخ استخدام')

    @property
    def get_experience(self):
        return datetime.datetime.now().year - self.hire_date.year

    DIPLOMA, ASSOCIATE, BACHELOR, MASTER, PHD = 'DP', 'AS', 'BA', 'MA', 'PHD'
    degree_choices = (
        (DIPLOMA, 'دیپلم'),
        (ASSOCIATE, 'فوق دیپلم'),
        (BACHELOR, 'لیسانس'),
        (MASTER, 'فوق لیسانس'),
        (PHD, 'دکتری')
    )
    education_degree = models.CharField(max_length=2, choices=degree_choices, verbose_name='مدرک تحصیلی')
    profession = models.ManyToManyField('Course', verbose_name='تخصص')

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class LevelField(models.Model):
    FIRST, SECOND, THIRD = 'first', 'second', 'third'
    level_choices = (
        (FIRST, 'اول'),
        (SECOND, 'دوم'),
        (THIRD, 'سوم')
    )
    level = models.CharField(max_length=10, choices=level_choices, default='first', verbose_name='پایه')
    MATH, NATURAL, HUMANITY = 'math', 'natural', 'humanity'
    field_choices = (
        (MATH, 'ریاضی'),
        (NATURAL, 'تجربی'),
        (HUMANITY, 'انسانی')
    )
    field = models.CharField(max_length=10, choices=field_choices, verbose_name='رشته', blank=True)

    def __str__(self):
        return self.get_level_display() + ' ' + self.get_field_display()


class Classroom(models.Model):
    level_field = models.ForeignKey('LevelField', on_delete=models.SET_NULL, null=True)
    A, B, C = 'a', 'b', 'c'
    branch_choices = (
        (A, 'الف'),
        (B, 'ب'),
        (C, 'ج')
    )
    branch = models.CharField(max_length=2, choices=branch_choices, default='a', null=True, verbose_name='گروه',
                              blank=True)
    education_year = models.CharField(max_length=20, null=True)
    courses = models.ManyToManyField('Course', through='TeacherClassCourse', related_name='classrooms')
    teachers = models.ManyToManyField('Teacher', through='TeacherClassCourse', related_name='classrooms')
    is_active = models.BooleanField(verbose_name='فعال')

    def __str__(self):
        return str(self.level_field) + ' ' + self.get_branch_display()


class Course(models.Model):
    name = models.CharField(max_length=20)
    level_field = models.ForeignKey('LevelField', on_delete=models.SET_NULL, null=True)
    unit = models.IntegerField()

    def __str__(self):
        return self.name


class StudentCourse(models.Model):
    student = models.ForeignKey('Student', related_name='student_courses', on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey('Course', related_name='student_courses', on_delete=models.SET_NULL, null=True)
    final_grade = models.FloatField(blank=True, null=True, validators=[
        MaxValueValidator(20), MinValueValidator(0)
    ])
    mid_grade = models.FloatField(blank=True, null=True, validators=[
        MaxValueValidator(20), MinValueValidator(0)
    ])


class Register(models.Model):
    student = models.ForeignKey('Student', related_name='registers', on_delete=models.SET_NULL, null=True,
                                verbose_name='دانش آموز')
    classroom = models.ForeignKey('Classroom', related_name='registers', on_delete=models.SET_NULL, null=True,
                                  verbose_name='کلاس')
    is_active = models.BooleanField(verbose_name='فعال')


class TeacherClassCourse(models.Model):
    teacher = models.ForeignKey('Teacher', related_name='teacher_class_courses', on_delete=models.SET_NULL, null=True,
                                verbose_name='معلم')
    classroom = models.ForeignKey('Classroom', related_name='teacher_class_courses', on_delete=models.SET_NULL,
                                  null=True, verbose_name='کلاس')
    course = models.ForeignKey('Course', related_name='teacher_class_courses', on_delete=models.SET_NULL, null=True,
                               verbose_name='دزس')
    class_time = models.ManyToManyField('ClassTime', related_name='teacher_class_course', verbose_name='زمان کلاس')

    def __str__(self):
        return str(self.classroom) + ' ' + str(self.course) + ' ' + str(self.teacher)


class ClassTime(models.Model):
    A, B, C, D = '1', '2', '3', '4'
    part_choices = (
        (A, 'زنگ اول'),
        (B, 'زنگ دوم'),
        (C, 'زنگ سوم'),
        (D, 'زنگ چهارم')
    )
    part = models.CharField(max_length=20, choices=part_choices, default='1', null=True, verbose_name='زنگ',
                            blank=True)
    Saturday, Sunday, Monday, Tuesday, Wednesday = 'Sa', 'Su', 'Mo', 'Tu', 'We'
    day_choices = (
        (Saturday, 'شنبه'),
        (Sunday, 'یکشنبه'),
        (Monday, 'دوشنبه'),
        (Tuesday, 'سه شنبه'),
        (Wednesday, 'چهارشنبه')
    )
    day = models.CharField(max_length=20, choices=day_choices, default='Sa', null=True, verbose_name='روز',
                           blank=True)

    def __str__(self):
        return self.get_day_display() + ' ' + self.get_part_display()


class Assignment(models.Model):
    file = models.FileField(upload_to='assignments')
    sent_time = models.DateField()
    deadline_time = models.DateField()
    teacher_class_course = models.ForeignKey(TeacherClassCourse, on_delete=models.SET_NULL, null=True)
    grade = models.IntegerField(null=True, blank=True, validators=[
        MaxValueValidator(20), MinValueValidator(0)
    ])
    description = models.TextField()


class StudentPresence(models.Model):
    student_course = models.ForeignKey(StudentCourse, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    presence = models.BooleanField(verbose_name='حضور')
    POSITIVE, NEGETIVE = 'pos', 'neg'
    activity_choices = (
        (POSITIVE, '+'),
        (NEGETIVE, '-')
    )
    activity = models.CharField(max_length=20, choices=activity_choices, null=True, blank=True, verbose_name='فعالیت')