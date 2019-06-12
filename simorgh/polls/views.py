from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic.edit import FormView, UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import ChoiceForm, ChoiceFormset
from .models import Choice, Question
from edu.models import Teacher, TeacherClassCourse, Student, Register


class ChoiceCreateView(UserPassesTestMixin, CreateView):
    model = Choice
    form_class = ChoiceForm

    def get_context_data(self, **kwargs):
        context = super(ChoiceCreateView, self).get_context_data(**kwargs)
        context['formset'] = ChoiceFormset()
        print(context['formset'].forms)
        context['questions'] = list(Question.objects.all())
        context['teacher'] = TeacherClassCourse.objects.get(id=self.kwargs['pk']).teacher
        return context

    def test_func(self):
        if Group.objects.get(name='student') in self.request.user.groups.all():
            register = Register.objects.get(student=self.request.user.student, is_active=True)
            tcc_list = TeacherClassCourse.objects.filter(classroom=register.classroom)
            tcc_id_list = [tcc.id for tcc in tcc_list]
            if int(self.kwargs['pk']) in tcc_id_list:
                print(True)
                return True
        else:
            if self.request.user.is_authenticated():
                raise Http404("شما نمی توانید در این نظرسنجی شرکت کنید.")

    def post(self, request, *args, **kwargs):
        formset = ChoiceFormset(request.POST)
        if formset.is_valid():
            return self.form_valid(formset)

    def form_valid(self, formset):
        if formset.is_valid():
            for i, form in enumerate(formset.forms):
                choice = form.save(commit=False)
                print(i)
                choice.question = Question.objects.get(id=i + 1)
                choice.student = self.request.user.student
                choice.teacher_class_course = TeacherClassCourse.objects.get(id=self.kwargs['pk'])
                choice.save()
            return HttpResponseRedirect('/polls/')
        return HttpResponseRedirect('/polls/{}'.format(self.kwargs['pk']))


class TeacherClassCourseListView(ListView):
    model = TeacherClassCourse
    template_name = 'polls/teacherclasscourse_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if Group.objects.get(name='student') in self.request.user.groups.all():
            student = Student.objects.get(user=self.request.user)
            register = Register.objects.get(student=student, is_active=True)
            tcc_passed_list = set(TeacherClassCourse.objects.filter(choice__student=self.request.user.student))
            tcc_passed_id_list = [tcc.id for tcc in tcc_passed_list]
            queryset = queryset.filter(classroom=register.classroom).exclude(id__in=tcc_passed_id_list)
        return queryset
