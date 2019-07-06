from itertools import chain

from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import ListAPIView

from .models import Student, Classroom, Teacher, StudentCourse, Course, TeacherClassCourse, \
    User, ClassTime, Register, Assignment, StudentPresence, TeacherPresence
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import StudentForm, TeacherSearchForm, TeacherForm, StudentSearchForm, \
    TeacherClassCourseForm, RegisterForm, ClassroomSearchForm, ClassroomForm, MessageForm, AssignmentForm, UserForm, \
    PlanningForm, StudentPresenceForm, StudentPresenceFormset, StudentUpdateForm, TeacherPresenceForm, ClassTimeForm, \
    TeacherPresenceFormset
from django.db.models import Q
import datetime
from .serializers import StudentSerializer, StudentCourseSerializer
from django.http import JsonResponse, Http404, HttpResponseRedirect
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
from django.urls import reverse_lazy, reverse
from directmessages.apps import Inbox
from directmessages.models import Message
import jdatetime

check_manager = user_passes_test(lambda u: Group.objects.get(name='manager') in u.groups.all())
check_teacher = user_passes_test(
    lambda u: any(
        [(Group.objects.get(name='teacher') in u.groups.all()),
         (Group.objects.get(name='manager') in u.groups.all())]
    )
)


@check_teacher
def student_class_list(request, pk):
    classroom = Classroom.objects.get(id=pk)
    if Group.objects.get(name='teacher') in request.user.groups.all():
        if Teacher.objects.get(user=request.user) not in Teacher.objects.filter(classrooms=classroom):
            raise Http404('شما به این کلاس دسترسی ندارید')
    classroom_students = list(Student.objects.filter(classrooms=classroom))
    return render(request, 'edu/student_class_list.html',
                  {'classroom_students': classroom_students, 'classroom': classroom})


@login_required
def teacher_class_list(request, pk):
    classroom = Classroom.objects.get(id=pk)
    if Group.objects.get(name='teacher') in request.user.groups.all():
        if Teacher.objects.get(user=request.user) not in Teacher.objects.filter(classrooms=classroom):
            raise Http404('شما به این کلاس دسترسی ندارید')
    if Group.objects.get(name='student') in request.user.groups.all():
        if Student.objects.get(user=request.user) not in Student.objects.filter(classrooms=classroom):
            raise Http404('شما به این کلاس دسترسی ندارید')
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
        Inbox.send_message(self.request.user, user, 'به پورتال آموزشی سیمرغ خوش آمدید')
        Inbox.send_message(self.request.user, user, 'لطفا پروفایل خود را کامل کنید.')
        return super().form_valid(form)


@method_decorator(check_manager, name='dispatch')
class StudentListView(ListView):
    model = Student
    form_class = StudentSearchForm

    def get_context_data(self, **kwargs):
        context = super(StudentListView, self).get_context_data(**kwargs)

        form_data = self.form_class()
        filter_dict = {}
        search_list = ['first_name', 'last_name', 'field']
        for item in search_list:
            filter_dict[item] = self.request.GET.get(item)
        form_data = self.form_class(initial=filter_dict)
        context.update({
            'search': form_data
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'pk' in self.kwargs.keys():
            queryset = Student.objects.filter(classrooms=Classroom.objects.get(id=self.kwargs['pk']))
        if self.request.GET:
            queryset = self.filter_queryset(queryset)
        return queryset

    def filter_queryset(self, queryset):
        filter_dict = {}
        search_list = ['first_name', 'last_name', 'field']
        for item in search_list:
            filter_dict[item] = self.request.GET.get(item)

        queryset = queryset.filter(
            user__first_name__icontains=filter_dict['first_name'],
            user__last_name__icontains=filter_dict['last_name'],
            registers__is_active=True,
            registers__classroom__level_field__field__icontains=filter_dict['field']
        )
        # queryset = register_list_queryset.filter(
        #     student__user__first_name__icontains=filter_dict['first_name']
        #     , student__user__last_name__icontains=filter_dict['last_name']
        # )
        print(queryset.values())
        return queryset


@method_decorator(check_manager, name='dispatch')
class StudentDetailView(DetailView):
    model = Student


@method_decorator(check_manager, name='dispatch')
class StudentUpdateView(UpdateView):
    model = Student
    fields = ['student_id']

    def get_form_class(self):
        return StudentUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def get_success_url(self):
        success_url = '/dashboard/studentlist'
        return success_url

    def form_valid(self, form):
        user_dict = {}
        for key in ['username', 'first_name', 'last_name', 'is_active']:
            user_dict[key] = form.cleaned_data.pop(key)
        my_user = Student.objects.get(id=self.kwargs['pk']).user
        my_user.username = user_dict['username']
        my_user.first_name = user_dict['first_name']
        my_user.last_name = user_dict['last_name']
        my_user.is_active = user_dict['is_active']
        my_user.save()
        form.save()
        return super().form_valid(form)



@method_decorator(check_manager, name='dispatch')
class StudentDeleteView(DeleteView):
    model = Student
    success_url = '/dashboard/studentlist'


# method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'edu/user_form.html'
    form_class = UserForm

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        tcc_list = []
        if Group.objects.get(name='teacher') in self.request.user.groups.all():
            teacher = Teacher.objects.get(user=self.request.user)
            tcc_list = list(TeacherClassCourse.objects.filter(teacher=teacher))
            for my_object in tcc_list:
                for class_time in list(ClassTime.objects.filter(teacher_class_course=my_object)):
                    context['part_day{}'.format(class_time.id)] = str(my_object.classroom) + ' ' + '({})'.format(
                        my_object.course)
        elif Group.objects.get(name='student') in self.request.user.groups.all():
            student = Student.objects.get(user=self.request.user)
            info = {}
            register = Register.objects.filter(student=student, is_active=True).first()
            info['level_field'] =register.classroom.level_field
            context['info'] = info
            tcc_list = list(TeacherClassCourse.objects.filter(classroom=register.classroom))
            for my_object in tcc_list:
                for class_time in list(ClassTime.objects.filter(teacher_class_course=my_object)):
                    context['part_day{}'.format(class_time.id)] = str(my_object.course) + ' ' + '({})'.format(
                        my_object.teacher.user.last_name)
        return context

    def get_success_url(self):
        success_url = '/dashboard'
        return success_url

    def test_func(self):
        if self.request.user.id == int(self.kwargs['pk']):
            return True
        else:
            if self.request.user.is_authenticated():
                raise Http404("You are not authenticated to edit this profile")

    def form_valid(self, form):
        print(form)
        form.save()
        return super().form_valid(form)


@method_decorator(check_manager, name='dispatch')
class TeacherListView(ListView):
    model = Teacher
    form_class = TeacherSearchForm

    def get_context_data(self, **kwargs):
        context = super(TeacherListView, self).get_context_data(**kwargs)
        hire_dates = []
        for teacher in context['teacher_list']:
            hire_dates.append(jdatetime.date.fromgregorian(date=teacher.hire_date))
        print(hire_dates)
        context.update({
            'search': self.form_class(),
            'hire_dates': hire_dates
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
        user = User.objects.create_user(password='abc123456', **user_dict)
        # user.set_password('abc123456')
        print(user.id)
        print(form.cleaned_data['hire_date'])
        my_teacher = form.save(commit=False)
        my_teacher.user = user
        my_teacher.save()
        Inbox.send_message(self.request.user, user, 'به پورتال آموزشی سیمرغ خوش آمدید')
        Inbox.send_message(self.request.user, user, 'لطفا پروفایل خود را کامل کنید.')
        # form.cleaned_data.update({'user': user})
        my_group = Group.objects.get(name='teacher')
        my_group.user_set.add(user)
        return super().form_valid(form)


@method_decorator(check_manager, name='dispatch')
class TeacherDeleteView(DeleteView):
    model = Teacher
    success_url = '/dashboard/teacherlist'


@method_decorator((login_required, csrf_exempt), name='dispatch')
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
        if Group.objects.get(name='teacher') in self.request.user.groups.all():
            queryset = queryset.filter(teachers=Teacher.objects.get(user=self.request.user), is_active=True)
        elif Group.objects.get(name='student') in self.request.user.groups.all():
            queryset = queryset.filter(registers=Register.objects.get(student__user=self.request.user), is_active=True)
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
    fields = ['branch', 'education_year', 'is_active']

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
    # success_url = reverse('edu:teacherclasscourse')
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
    return render(request, 'edu/dashboard.html', {'user': user})


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
    student_number = classroom.students.count()
    context['student_number'] = student_number
    for my_object in list(TeacherClassCourse.objects.filter(classroom=classroom)):
        for class_time in list(ClassTime.objects.filter(teacher_class_course=my_object)):
            context['part_day{}'.format(class_time.id)] = str(my_object.course) + ' ' + '({})'.format(
                my_object.teacher.user.last_name)
    return render(request, 'edu/weekly_schedule.html', context)


class MessageListView(ListView):
    model = Message
    template_name = 'edu/dashboard.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(recipient=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        message_list = list(context['message_list'])
        # for message in message_list:
        #     message.sent_at = jdatetime.date.fromgregorian(datetime=message.sent_at.datetime)
        #     print(message.sent_at)
        # print(message_list[0].sent_at)
        return context


class AssignmentListView(ListView):
    model = Assignment
    template_name = 'edu/assignment_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if Group.objects.get(name='teacher') in self.request.user.groups.all():
            queryset = queryset.filter(teacher_class_course__teacher__user=self.request.user)
        elif Group.objects.get(name='student') in self.request.user.groups.all():
            queryset = queryset.filter(teacher_class_course__classroom__students=self.request.user.student)
        return queryset


@method_decorator(check_teacher, name='dispatch')
class AssignmentCreateView(SuccessMessageMixin, CreateView):
    template_name = 'edu/assignment_form.html'
    form_class = AssignmentForm
    success_url = '/dashboard/assignmentlist/'
    success_message = 'با موفقیت ثبت شد'

    def form_valid(self, form):
        assignment = form.save(commit=False)
        assignment.sent_time = datetime.datetime.now()
        assignment.save()
        for student in list(assignment.teacher_class_course.classroom.students.all()):
            Inbox.send_message(self.request.user, student.user, assignment.description)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@check_teacher
def send_message_view(request):
    if request.method == 'POST':
        form = MessageForm(request, request.POST)
        if form.is_valid():
            for recipient in form.cleaned_data['recipients']:
                Inbox.send_message(request.user, recipient, form.cleaned_data['content'])
            messages.add_message(request, messages.SUCCESS, 'با موفقیت ارسال شد.')
            return HttpResponseRedirect(reverse('edu:message_form'))
    else:
        form = MessageForm(request, request.POST)
        print(form.fields['recipients'])
    return render(request, 'edu/message_form.html', {'form': form})


@method_decorator(check_teacher, name='dispatch')
class TeacherClassCourseListView(ListView):
    model = TeacherClassCourse
    template_name = 'edu/teacherclasscourse_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if Group.objects.get(name='teacher') in self.request.user.groups.all():
            queryset = queryset.filter(teacher__user=self.request.user)
        return queryset


@method_decorator(check_teacher, name='dispatch')
class StudentCourseListView(UserPassesTestMixin, ListView):
    model = StudentCourse
    template_name = 'edu/studentcourse_list.html'

    def test_func(self):
        if Group.objects.get(name='teacher') in self.request.user.groups.all():
            pk_tcc = self.kwargs.get('pk_tcc', '')
            teacher_class_course = TeacherClassCourse.objects.get(id=pk_tcc)
            if teacher_class_course.teacher != Teacher.objects.get(user=self.request.user):
                raise Http404("شما به این لیست دسترسی ندارید.")
        return True

    def get_queryset(self):
        queryset = super().get_queryset()
        pk_tcc = self.kwargs.get('pk_tcc', '')
        print(pk_tcc)
        teacher_class_course = TeacherClassCourse.objects.get(id=pk_tcc)
        queryset = queryset.filter(
            course=teacher_class_course.course, student__registers__classroom=teacher_class_course.classroom
        )
        return queryset


@method_decorator(check_teacher, name='dispatch')
class StudentCourseUpdateView(SuccessMessageMixin, UpdateView):
    model = StudentCourse
    fields = ['mid_grade', 'final_grade']
    success_message = 'با موفقیت ثبت شد'

    def get_success_url(self):
        student_course = StudentCourse.objects.get(id=self.kwargs['pk'])
        teacher_class_course = TeacherClassCourse.objects.get(
            course=student_course.course, classroom=student_course.student.registers.get(is_active=True).classroom
        )
        success_url = '/dashboard/activity/grade/{}/students'.format(teacher_class_course.id)
        return success_url


import random
from deap import base
from deap import creator
from deap import tools


def ga_planning(info):
    ind_size = 0
    for tcc in info:
        ind_size += tcc['time_number']
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 4)
    toolbox.register("individual", tools.initRepeat, creator.Individual,
                     toolbox.attr_bool, ind_size)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evalOneMax(individual):
        OF = 0
        c = 0
        for tcc in info:
            for num in range(0, tcc['time_number']):
                if str(individual[c]) not in tcc['days']:
                    OF += -100
                c += 1
        for i in range(0, 5):
            if individual.count(i) > 4:
                OF += -10000
        return OF,

    toolbox.register("evaluate", evalOneMax)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    random.seed(64)
    pop = toolbox.population(n=300)
    CXPB, MUTPB = 0.5, 0.2
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    fits = [ind.fitness.values[0] for ind in pop]
    g = 0
    while max(fits) != 0 and g < 200:
        g = g + 1
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring
        fits = [ind.fitness.values[0] for ind in pop]
        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5

    best_ind = tools.selBest(pop, 1)[0]
    return best_ind


def planning_view(request):
    PlanningFormSet = formset_factory(PlanningForm, extra=12)
    if request.method == 'POST':
        formset = PlanningFormSet(request.POST, request.FILES)
        info = []
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data != {}:
                    info.append(form.cleaned_data)

        best_planning = ga_planning(info)
        print(best_planning)
        context = {}
        class_time = [1, 1, 1, 1, 1]
        unauthorized_time = [0 for i in range(0, 20)]
        c = 0
        for tcc in info:
            for i in range(0, tcc['time_number']):
                context['part_day{}'.format(4 * best_planning[c] + class_time[best_planning[c]])] = str(
                    tcc['course']) + ' ' + '({})'.format(
                    tcc['teacher'].user.last_name)
                if str(best_planning[c]) not in tcc['days']:
                    unauthorized_time[4 * best_planning[c] + class_time[best_planning[c]] - 1] = 1
                class_time[best_planning[c]] += 1
                c += 1
        context['unauthorized_time'] = unauthorized_time
        context['info'] = info
        print(info)
        print(best_planning)
        print(best_planning.fitness.values)
        print(unauthorized_time)
        return render(request, 'edu/weekly_schedule.html', context)


    else:
        formset = PlanningFormSet()
    return render(request, 'edu/planning_form.html', {'formset': formset})


@method_decorator(check_teacher, name='dispatch')
class StudentPresenceListView(UserPassesTestMixin, ListView):
    model = StudentPresence
    template_name = 'edu/student_presence_list.html'

    def test_func(self):

        return True

    def get_student_course_list(self):
        pk_tcc = self.kwargs.get('pk_tcc', '')
        teacher_class_course = TeacherClassCourse.objects.get(id=pk_tcc)
        student_course_list = list(StudentCourse.objects.filter(
            course=teacher_class_course.course, student__registers__classroom=teacher_class_course.classroom
        ))
        return student_course_list

    def get_queryset(self):
        queryset = super().get_queryset()
        student_course_list = self.get_student_course_list()
        queryset = queryset.filter(student_course__in=student_course_list)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(StudentPresenceListView, self).get_context_data(**kwargs)
        pk_tcc = self.kwargs.get('pk_tcc', '')
        teacher_class_course = TeacherClassCourse.objects.get(id=pk_tcc)
        context['tcc'] = teacher_class_course
        presence_list = context['object_list']
        date_list = presence_list.order_by().values('date').distinct()

        student_course_list = self.get_student_course_list()
        presence_date_list = []
        for student_course in student_course_list:
            presence_date = {}
            presence_date['student_course'] = student_course
            presence_date['student_presence_list'] = []
            for date in date_list:
                try:
                    presence_date['student_presence_list'].append(
                        StudentPresence.objects.get(student_course=student_course, date=date['date']))
                except:
                    presence_date['student_presence_list'].append(None)
            presence_date_list.append(presence_date)
        context['presence_date_list'] = presence_date_list
        date_list = [jdatetime.date.fromgregorian(date=date['date']) for date in date_list]
        print(presence_date_list)
        context['date_list'] = date_list
        # print(context['presence_date_list'])
        return context


@method_decorator(check_teacher, name='dispatch')
class StudentPresenceCreateView(UserPassesTestMixin, CreateView):
    model = StudentPresence
    form_class = StudentPresenceForm

    def get_student_course_list(self):
        pk_tcc = self.kwargs.get('pk_tcc', '')
        teacher_class_course = TeacherClassCourse.objects.get(id=pk_tcc)
        student_course_list = list(StudentCourse.objects.filter(
            course=teacher_class_course.course, student__registers__classroom=teacher_class_course.classroom
        ))
        return student_course_list

    def get_context_data(self, **kwargs):
        context = super(StudentPresenceCreateView, self).get_context_data(**kwargs)
        student_course_list = self.get_student_course_list()
        StudentPresenceFormset = formset_factory(StudentPresenceForm, extra=len(student_course_list))
        context['formset'] = StudentPresenceFormset()
        context['students'] = [student_course.student for student_course in student_course_list]
        return context

    def test_func(self):
        # if Group.objects.get(name='student') in self.request.user.groups.all():
        #     register = Register.objects.get(student=self.request.user.student, is_active=True)
        #     tcc_list = TeacherClassCourse.objects.filter(classroom=register.classroom)
        #     tcc_id_list = [tcc.id for tcc in tcc_list]
        #     if int(self.kwargs['pk']) in tcc_id_list:
        #         print(True)
        #         return True
        # else:
        #     if self.request.user.is_authenticated():
        #         raise Http404("شما نمی توانید در این نظرسنجی شرکت کنید.")
        return True

    def post(self, request, *args, **kwargs):
        formset = StudentPresenceFormset(request.POST)
        if formset.is_valid():
            return self.form_valid(formset)

    def form_valid(self, formset):
        if formset.is_valid():
            student_course_list = self.get_student_course_list()
            for i, form in enumerate(formset.forms):
                student_presence = form.save(commit=False)
                if student_presence.presence == None:
                    student_presence.presence = False
                student_presence.date = datetime.date.today()
                student_presence.student_course = student_course_list[i]
                student_presence.save()
            return HttpResponseRedirect('/dashboard/activity/presence/{}'.format(self.kwargs['pk_tcc']))
        return HttpResponseRedirect('/dashboard/activity/presence/{}/create'.format(self.kwargs['pk_day']))


@method_decorator(check_manager, name='dispatch')
class TeacherPresenceCreateView(CreateView):
    model = TeacherPresence
    form_class = TeacherPresenceForm

    def get_context_data(self, **kwargs):
        context = super(TeacherPresenceCreateView, self).get_context_data(**kwargs)
        print(self.kwargs['pk_day'])
        days = ['Sa', 'Su', 'Mo', 'Tu', 'We']
        tcc_list = list(TeacherClassCourse.objects.filter(class_time__day=days[int(self.kwargs['pk_day'])]))
        TeacherPresenceFormset = formset_factory(TeacherPresenceForm, extra=len(tcc_list))
        context['formset'] = TeacherPresenceFormset()
        context['tcc'] = tcc_list
        return context

    def post(self, request, *args, **kwargs):
        formset = TeacherPresenceFormset(request.POST)
        if formset.is_valid():
            return self.form_valid(formset)

    def form_valid(self, formset):
        if formset.is_valid():
            days = ['Sa', 'Su', 'Mo', 'Tu', 'We']
            tcc_list = list(TeacherClassCourse.objects.filter(class_time__day=days[int(self.kwargs['pk_day'])]))
            for i, form in enumerate(formset.forms):
                teacher_presence = form.save(commit=False)
                print(teacher_presence)
                if teacher_presence.presence == None:
                    teacher_presence.presence = False
                teacher_presence.date = datetime.date.today()
                teacher_presence.teacher_class_course = tcc_list[i]
                teacher_presence.save()
            return HttpResponseRedirect('/dashboard/activity/teacher_presence/')
        return HttpResponseRedirect('/dashboard/activity/teacher_presence/{}/create'.format(self.kwargs['pk_day']))


@method_decorator(check_manager, name='dispatch')
class TeacherPresenceListView(ListView):
    model = TeacherPresence
    template_name = 'edu/teacher_presence_list.html'


    def get_context_data(self, **kwargs):
        context = super(TeacherPresenceListView, self).get_context_data(**kwargs)
        tcc_list = list(TeacherClassCourse.objects.all())
        teacher_presence_list = []
        for tcc in tcc_list:
            teacher_presence = {}
            teacher_presence['tcc'] = tcc
            teacher_presence['presence_list'] = list(TeacherPresence.objects.filter(teacher_class_course= tcc))
            teacher_presence_list.append(teacher_presence)
        context['teacher_presence_list'] = teacher_presence_list
        return context


class StudentCourseListAPIView(ListAPIView):
    serializer_class = StudentCourseSerializer
    # model = StudentCourse
    paginate_by = 20

    def get_queryset(self):
        pk = self.kwargs['pk']
        student = Student.objects.get(pk=pk)
        classroom = Classroom.objects.filter(students=student, is_active=True).first()
        course_list = list(Course.objects.filter(classrooms=classroom))
        student_courses = StudentCourse.objects.filter(course__in=course_list, student=student)
        teachers = Teacher.objects.filter(teacher_class_courses__classroom=classroom,
                                          teacher_class_courses__course__in=course_list)
        queryset = chain(student_courses, teachers)
        print(teachers)
        print(student_courses)
        return student_courses
