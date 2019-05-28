from django.shortcuts import render, redirect
from .models import Student, Classroom, Teacher, StudentCourse, Course, TeacherClassCourse, User, ClassTime
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import StudentForm, TeacherSearchForm, TeacherForm, StudentSearchForm, \
    TeacherClassCourseForm, RegisterForm, ClassroomSearchForm, ClassroomForm
from django.db.models import Q
import datetime
from .serializers import StudentSerializer
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.urls import reverse_lazy

check_manager = user_passes_test(lambda u: Group.objects.get(name='manager') in u.groups.all())
check_teacher = user_passes_test(
    lambda u: any(
        [(Group.objects.get(name='teacher') in u.groups.all()),
         (Group.objects.get(name='manager') in u.groups.all())]
    )
)


def student_class_list(request, pk):
    classroom = Classroom.objects.get(id=pk)
    classroom_students = list(Student.objects.filter(classrooms=classroom))
    return render(request, 'edu/student_class_list.html',
                  {'classroom_students': classroom_students, 'classroom': classroom})


def teacher_class_list(request, pk):
    classroom = Classroom.objects.get(id=pk)
    classroom_teacher_course = list(TeacherClassCourse.objects.filter(classroom=classroom))
    return render(request, 'edu/teacher_class_list.html',
                  {'classroom_teacher_course': classroom_teacher_course, 'classroom': classroom})


@method_decorator(check_manager, name='dispatch')
class StudentCreateView(CreateView):
    template_name = 'edu/student_form.html'
    form_class = StudentForm
    success_url = '/dashboard/studentlist/'

    def form_valid(self, form):
        student_id = form.cleaned_data.pop('student_id')
        user = form.save()
        user.set_password('abc123456')
        Student.objects.create(student_id=student_id, user=user, last_modified_date=datetime.datetime.now())
        my_group = Group.objects.get(name='student')
        my_group.user_set.add(user)
        return super().form_valid(form)


@method_decorator(check_manager, name='dispatch')
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


@method_decorator(check_manager, name='dispatch')
class StudentDetailView(DetailView):
    model = Student


@method_decorator(check_manager, name='dispatch')
class StudentUpdateView(UpdateView):
    model = Student
    fields = ['student_id']

    def get_success_url(self):
        success_url = '/dashboard/studentlist'
        return success_url


@method_decorator(check_manager, name='dispatch')
class StudentDeleteView(DeleteView):
    model = Student
    success_url = '/dashboard/studentlist'


class ProfileUpdateView(UpdateView):
    model = User
    fields = ['username', 'password', 'email']
    template_name = 'edu/profile.html'

    def get_success_url(self):
        return '/dashboard/profile'


@method_decorator(check_manager, name='dispatch')
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


@method_decorator(check_manager, name='dispatch')
class TeacherDetailView(DetailView):
    model = Teacher


@method_decorator(check_manager, name='dispatch')
class TeacherUpdateView(UpdateView):
    model = Teacher
    fields = ['hire_date', 'education_degree']

    def get_success_url(self):
        success_url = '/dashboard/teacherlist'
        return success_url


@method_decorator(check_manager, name='dispatch')
class TeacherCreateView(CreateView):
    template_name = 'edu/teacher_form.html'
    form_class = TeacherForm
    success_url = '/dashboard/teacherlist/'

    def form_valid(self, form):
        user_dict = {}
        for key in ['username', 'first_name', 'last_name', 'is_active']:
            user_dict[key] = form.cleaned_data.pop(key)
        user = User.objects.create_user(**user_dict)
        user.set_password('abc123456')
        print(user.id)
        my_teacher = form.save(commit=False)
        my_teacher.user = user
        my_teacher.save()
        # form.cleaned_data.update({'user': user})
        my_group = Group.objects.get(name='teacher')
        my_group.user_set.add(user)
        return super().form_valid(form)


@method_decorator(check_manager, name='dispatch')
class TeacherDeleteView(DeleteView):
    model = Teacher
    success_url = '/dashboard/teacherlist'


@method_decorator(check_teacher, name='dispatch')
class ClassroomListView(ListView):
    model = Classroom
    form_class = ClassroomSearchForm

    def get_context_data(self, **kwargs):
        context = super(ClassroomListView, self).get_context_data(**kwargs)
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
        search_list = ['level', 'field', 'branch', 'education_year']
        for item in search_list:
            filter_dict[item] = self.request.GET.get(item)

        queryset = queryset.filter(
            Q(level_field__level__icontains=filter_dict['level'])
            & Q(level_field__field__icontains=filter_dict['field'])
            & Q(branch__icontains=filter_dict['branch'])
            & Q(education_year__icontains=filter_dict['education_year'])
        )
        return queryset


@method_decorator(check_manager, name='dispatch')
class ClassroomDetailView(DetailView):
    model = Classroom


@method_decorator(check_manager, name='dispatch')
class ClassroomUpdateView(UpdateView):
    model = Classroom
    fields = ['branch', 'education_year']

    def get_success_url(self):
        success_url = '/dashboard/classroomlist/'
        return success_url


@method_decorator(check_manager, name='dispatch')
class ClassroomCreateView(CreateView):
    template_name = 'edu/classroom_form.html'
    form_class = ClassroomForm
    success_url = '/dashboard/classroomlist/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@method_decorator(check_manager, name='dispatch')
class ClassroomDeleteView(DeleteView):
    model = Classroom
    success_url = '/dashboard/classroomlist'


@method_decorator(check_manager, name='dispatch')
class TeacherClassCourseCreateView(SuccessMessageMixin, CreateView):
    template_name = 'edu/teacherclasscourse_form.html'
    form_class = TeacherClassCourseForm
    #success_url = reverse('edu:teacherclasscourse')
    success_message = 'با موفقیت ثبت شد'

    def get_success_url(self):
        return reverse_lazy('edu:classroom_teachers', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(TeacherClassCourseCreateView, self).get_context_data(**kwargs)
        classroom = Classroom.objects.get(id=self.kwargs['pk'])
        object_list = []
        for my_object in list(TeacherClassCourse.objects.filter(classroom=classroom)):
            object_list.append(my_object)
        time_list = list(ClassTime.objects.filter(~Q(teacher_class_course__in=object_list)))
        print(time_list)
        context.update({
            'classroom': Classroom.objects.get(id=self.kwargs['pk'])
        })
        return context

    def form_valid(self, form):
        my_teacher_course = form.save(commit=False)
        my_teacher_course.classroom = Classroom.objects.get(id=self.kwargs['pk'])
        my_teacher_course.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs


@method_decorator(check_manager, name='dispatch')
class RegisterCreateView(SuccessMessageMixin, CreateView):
    template_name = 'edu/register_form.html'
    form_class = RegisterForm
    success_url = '/dashboard/studentregister/'
    success_message = 'با موفقیت ثبت شد'

    def form_valid(self, form):
        form.save()
        for course in Course.objects.filter(classrooms=form.cleaned_data['classroom']):
            my_student_course = StudentCourse.objects.get_or_create(student=form.cleaned_data['student'], course=course)
        return super().form_valid(form)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def student_list_api(request):
    if request.method == 'GET':
        students = Student.objects.all()
        student_serializer = StudentSerializer(students, many=True)
        return JsonResponse(student_serializer.data, safe=False)


@login_required
def login_view(request):
    user = request.user
    return render(request, 'index.html', {'user': user})


def error_404_view(request, exception):
    return render(request, '404.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    print(form)
    return render(request, 'edu/change_password.html', {
        'form': form
    })

def weekly_schedule(request, pk):
    classroom = Classroom.objects.get(id=pk)
    context = {}
    context['classroom'] = classroom
    for my_object in list(TeacherClassCourse.objects.filter(classroom=classroom)):
        for class_time in list(ClassTime.objects.filter(teacher_class_course=my_object)):
            context['part_day{}'.format(class_time.id)] = str(my_object.course) + ' ' + '({})'.format(my_object.teacher.user.last_name)
    return render(request, 'edu/weekly_schedule.html', context)