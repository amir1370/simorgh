from django.shortcuts import render
from .models import Student, Classroom, Teacher
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import StudentForm, TeacherSearchForm
from django.db.models import Q
import datetime


def class_list(request, class_id):
    classroom = Classroom.objects.filter(id=class_id).first()
    classroom_students = list(Student.objects.filter(classroom=classroom))
    return render(request, 'edu/student_list.html', {'classroom_student': classroom_students})


class FormViewStudent(FormView):
    template_name = 'edu/student_form.html'
    form_class = StudentForm
    success_url = '/class/home/studentform/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class StudentListView(ListView):
    model = Student


class StudentDetailView(DetailView):
    model = Student


class StudentUpdateView(UpdateView):
    model = Student
    fields = ['student_id']


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
            # print(self.request.GET)
            # first_name = self.request.GET.get('first_name')
            # last_name = self.request.GET.get('last_name')
            # queryset = queryset.filter(
            #     Q(user__first_name__icontains= first_name)|Q(user__last_name__icontains= last_name)
            # )
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


class TeacherDetailView(DetailView):
    model = Teacher


class TeacherUpdateView(UpdateView):
    model = Teacher
    fields = ['hire_date', 'education_degree']


class ClassroomListView(ListView):
    model = Classroom


class ClassroomDetailView(DetailView):
    model = Classroom


class ClassroomUpdateView(UpdateView):
    model = Classroom
    fields = ['branch', 'education_year']
