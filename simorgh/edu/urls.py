from django.conf.urls import url, handler404
from . import views
from django.contrib.auth import views as auth_views

app_name = 'edu'
urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html', redirect_field_name='index.html')),
    url(r'^logout/$', auth_views.LogoutView.as_view(redirect_field_name='login.html'), name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^dashboard/$', views.login_view),
    url(r'^dashboard/studentform/$', views.StudentCreateView.as_view()),
    url(r'^dashboard/profile/(?P<pk>[0-9]+)/$', views.ProfileUpdateView.as_view(), name='profile'),
    url(r'^dashboard/studentlist/$', views.StudentListView.as_view(), name='studentlist'),
    url(r'^dashboard/students/(?P<pk>[0-9]+)/$', views.StudentDetailView.as_view(), name='studentdetail'),
    url(r'^dashboard/students/(?P<pk>[0-9]+)/edit$', views.StudentUpdateView.as_view(), name='studentedit'),
    url(r'^dashboard/students/(?P<pk>[0-9]+)/delete$', views.StudentDeleteView.as_view(), name='studentdelete'),
    url(r'^dashboard/teacherlist/$', views.TeacherListView.as_view(), name='teacherlist'),
    url(r'^dashboard/teacherform/$', views.TeacherCreateView.as_view()),
    url(r'^dashboard/teachers/(?P<pk>[0-9]+)/$', views.TeacherDetailView.as_view(), name='tacherdetail'),
    url(r'^dashboard/teachers/(?P<pk>[0-9]+)/edit$', views.TeacherUpdateView.as_view(), name='teacheredit'),
    url(r'^dashboard/teachers/(?P<pk>[0-9]+)/delete$', views.TeacherDeleteView.as_view(), name='teacherdelete'),
    url(r'^dashboard/classroomlist/$', views.ClassroomListView.as_view(), name='classroomlist'),
    url(r'^dashboard/classroomform/$', views.ClassroomCreateView.as_view()),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/$', views.ClassroomDetailView.as_view(), name='classroomdetail'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/edit$', views.ClassroomUpdateView.as_view(), name='classroomedit'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/delete$', views.ClassroomDeleteView.as_view(), name='classroomdelete'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/students$', views.student_class_list, name='classroom_students'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/teachers$', views.teacher_class_list, name='classroom_teachers'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/teachercourse$', views.TeacherClassCourseCreateView.as_view(), name='teacherclasscourse'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9]+)/schedule$', views.weekly_schedule, name='weekly_schedule'),
    url(r'^dashboard/studentregister/$', views.RegisterCreateView.as_view(), name='student_register'),
    url(r'students/api/$', views.student_list_api)
]
handler404 = 'views.error_404_view'
