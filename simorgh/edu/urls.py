from django.conf import settings
from django.conf.urls import url, handler404
from django.conf.urls.static import static
from django.shortcuts import redirect

from . import views
from django.contrib.auth import views as auth_views
from .models import Student, Classroom


def login_user_redirect(function):
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.user.is_authenticated:
            return redirect('edu:messagelist')
        return function(*args, **kwargs)

    return wrapper


app_name = 'edu'
urlpatterns = [
    url(r'^login/$', login_user_redirect(
        auth_views.LoginView.as_view(template_name='login.html', redirect_field_name='edu/dashboard.html'))),
    url(r'^logout/$', auth_views.LogoutView.as_view(redirect_field_name='login.html'), name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^dashboard/$', views.MessageListView.as_view(), name='messagelist'),
    url(r'^dashboard/profile/(?P<pk>[0-9]+)/$', views.ProfileUpdateView.as_view(), name='profile'),
]
urlpatterns += [
    url(r'^dashboard/studentform/$', views.StudentCreateView.as_view()),
    url(r'^dashboard/studentlist/$', views.StudentListView.as_view(), name='studentlist'),
    url(r'^dashboard/students/(?P<pk>[0-9]+)/$', views.StudentDetailView.as_view(), name='studentdetail'),
    url(r'^dashboard/students/(?P<pk>[0-9]+)/edit$', views.StudentUpdateView.as_view(), name='studentedit'),
    url(r'^dashboard/students/(?P<pk>[0-9]+)/delete$', views.StudentDeleteView.as_view(), name='studentdelete'),
    url(r'^dashboard/studentregister/$', views.RegisterCreateView.as_view(), name='student_register'),
    url(r'students/api/$', views.student_list_api),
    url(r'students/studentcourse/api/(?P<pk>[0-9]+)$', views.StudentCourseListAPIView.as_view()),
]
urlpatterns += [
    url(r'^dashboard/teacherlist/$', views.TeacherListView.as_view(), name='teacherlist'),
    url(r'^dashboard/teacherform/$', views.TeacherCreateView.as_view()),
    url(r'^dashboard/teachers/(?P<pk>[0-9]+)/$', views.TeacherDetailView.as_view(), name='tacherdetail'),
    url(r'^dashboard/teachers/(?P<pk>[0-9]+)/edit$', views.TeacherUpdateView.as_view(), name='teacheredit'),
    url(r'^dashboard/teachers/(?P<pk>[0-9]+)/delete$', views.TeacherDeleteView.as_view(), name='teacherdelete'),
]
urlpatterns += [
    url(r'^dashboard/classroomlist/$', views.ClassroomListView.as_view(), name='classroomlist'),
    url(r'^dashboard/classroomform/$', views.ClassroomCreateView.as_view()),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/$', views.ClassroomDetailView.as_view(), name='classroomdetail'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/edit$', views.ClassroomUpdateView.as_view(), name='classroomedit'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/delete$', views.ClassroomDeleteView.as_view(), name='classroomdelete'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/students$', views.student_class_list, name='classroom_students'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/teachers$', views.teacher_class_list, name='classroom_teachers'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/teachercourse$', views.TeacherClassCourseCreateView.as_view(),
        name='teacherclasscourse'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/schedule$', views.weekly_schedule, name='weekly_schedule'),
]
urlpatterns += [
    url(r'^dashboard/assignmentlist/$', views.AssignmentListView.as_view(), name='assignmentlist'),
    url(r'^dashboard/assignmentform/$', views.AssignmentCreateView.as_view()),
]
urlpatterns += [
    url(r'^dashboard/activity/$', views.TeacherClassCourseListView.as_view(), name='activity'),
    url(r'^dashboard/activity/grade/(?P<pk_tcc>[0-9]+)/students$', views.StudentCourseListView.as_view(),
        name='students_grade'),
    url(r'^dashboard/activity/grade/(?P<pk>[0-9]+)/edit$', views.StudentCourseUpdateView.as_view(), name='grade_edit'),
    url(r'^dashboard/activity/presence/(?P<pk_tcc>[0-9]+)/create$', views.StudentPresenceCreateView.as_view(),
        name='student_presence_create'),
    url(r'^dashboard/activity/presence/(?P<pk_tcc>[0-9]+)$', views.StudentPresenceListView.as_view(),
        name='student_presence_list'),
    url(r'^dashboard/activity/teacher_presence/(?P<pk_day>[0-4])/create$', views.TeacherPresenceCreateView.as_view(),
        name='teacher_presence_create'),
    url(r'^dashboard/activity/teacher_presence$', views.TeacherPresenceListView.as_view(),
        name='teacher_presence_list'),
]
urlpatterns += [
    url(r'^dashboard/messageform/$', views.send_message_view, name='message_form'),
    url(r'^dashboard/planning/$', views.planning_view, name='planning'),
]
handler404 = 'views.error_404_view'
