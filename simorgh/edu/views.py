from django.shortcuts import render
from .models import Student, Classroom, Teacher, StudentCourse, Course
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import StudentForm, TeacherSearchForm, TeacherForm, StudentSearchForm, TeacherClassCourseForm, RegisterForm
from django.db.models import Q
import datetime
from .serializers import StudentSerializer
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin


manager_decorator = method_decorator(
    user_passes_test(lambda u: Group.objects.get(name='manager') in u.groups.all()), name='dispatch'
)


def class_list(request, class_id):
    classroom = Classroom.objects.filter(id=class_id).first()
    classroom_students = list(Student.objects.filter(classroom=classroom))
    return render(request, 'edu/student_list.html', {'classroom_student': classroom_students})

@manager_decorator
class FormViewStudent(FormView):
    template_name = 'edu/student_form.html'
    form_class = StudentForm
    success_url = '/dashboard/studentlist/'

    def form_valid(self, form):
        form.save()
        my_group = Group.objects.get(name='student')
        my_group.user_set.add(form.cleaned_data['user'])
        return super().form_valid(form)


@manager_decorator
class StudentListView(ListView):
    model = Student
    form_class = StudentSearchForm

    def get_context_data(self, **kwargs):
        context = super(StudentListView, self).get_context_data(**kwargs)
        context.update({
            'search': self.form_class()
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET:
            queryset = self.filter_queryset(queryset)
        return queryset

    def filter_queryset(self, queryset):
        filter_dict = {}
        search_list = ['first_name', 'last_name']
        for item in search_list:
            filter_dict[item] = self.request.GET.get(item)

        queryset = queryset.filter(
            Q(user__first_name__icontains=filter_dict['first_name'])
            & Q(user__last_name__icontains=filter_dict['last_name'])
        )
        return queryset


@manager_decorator
class StudentDetailView(DetailView):
    model = Student

@manager_decorator
class StudentUpdateView(UpdateView):
    model = Student
    fields = ['student_id']


@manager_decorator
class TeacherListView(ListView):
    model = Teacher
    form_class = TeacherSearchForm


    def get_context_data(self, **kwargs):
        context = super(TeacherListView, self).get_context_data(**kwargs)
        context.update({
            'search': self.form_class()
        })
        # print(context['teacher_list'][0].hire_date)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET:

            queryset = self.filter_queryset(queryset)
        return queryset

    def filter_queryset(self, queryset):
        filter_dict = {}
        search_list = ['first_name', 'last_name', 'from_hire_date', 'to_hire_date', 'education_degree']
        for item in search_list:
            filter_dict[item] = self.request.GET.get(item)

        if filter_dict['to_hire_date'] == '':
            filter_dict['to_hire_date'] = datetime.date.today()
        if filter_dict['from_hire_date'] == '':
            filter_dict['from_hire_date'] = '2000-01-01'
        queryset = queryset.filter(
            Q(user__first_name__icontains=filter_dict['first_name'])
            & Q(user__last_name__icontains=filter_dict['last_name'])
            & Q(hire_date__gte=filter_dict['from_hire_date'])
            & Q(hire_date__lte=filter_dict['to_hire_date'])
            & Q(education_degree__icontains=filter_dict['education_degree'])
        )
        return queryset


@manager_decorator
class TeacherDetailView(DetailView):
    model = Teacher


@manager_decorator
class TeacherUpdateView(UpdateView):
    model = Teacher
    fields = ['hire_date', 'education_degree']


@manager_decorator
class TeacherCreateView(CreateView):
    template_name = 'edu/teacher_form.html'
    form_class = TeacherForm
    success_url = '/dashboard/teacherlist/'

    def form_valid(self, form):
        form.save()
        my_group = Group.objects.get(name='teacher')
        my_group.user_set.add(form.cleaned_data['user'])
        return super().form_valid(form)

@manager_decorator
class ClassroomListView(ListView):
    model = Classroom

@manager_decorator
class ClassroomDetailView(DetailView):
    model = Classroom

@manager_decorator
class ClassroomUpdateView(UpdateView):
    model = Classroom
    fields = ['branch', 'education_year']


class TeacherClassCourseCreateView(SuccessMessageMixin, CreateView):
    template_name = 'edu/teacherclasscourse_form.html'
    form_class = TeacherClassCourseForm
    success_url = '/dashboard/teacherclasscourse/'
    success_message = 'با موفقیت ثبت شد'


    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class RegisterCreateView(SuccessMessageMixin, CreateView):
    template_name = 'edu/register_form.html'
    form_class = RegisterForm
    success_url = '/dashboard/studentregister/'
    success_message = 'با موفقیت ثبت شد'

    def form_valid(self, form):
        form.save()
        for course in Course.objects.filter(classrooms=form.cleaned_data['classroom']):
            my_student_course = StudentCourse.objects.create(student=form.cleaned_data['student'], course=course)
        print(form.cleaned_data)
        return super().form_valid(form)



def student_list_api(request):
    if request.method == 'GET':
        students = Student.objects.all()
        student_serializer = StudentSerializer(students, many=True)
        return JsonResponse(student_serializer.data, safe=False)

@login_required
def login_view(request):
    user = request.user
    return render(request, 'index.html', {'user': user})


def logout_view(request):
    logout(request)
