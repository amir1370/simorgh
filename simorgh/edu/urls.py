from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

app_name = 'edu'
urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html', redirect_field_name='index.html')),
    url(r'^logout/$', auth_views.LogoutView.as_view(redirect_field_name='login.html'), name='logout'),
    url(r'^dashboard/$', views.login_view),
    url(r'^(?P<class_id>[0-9])+/$', views.class_list),
    url(r'^dashboard/studentform/$', views.FormViewStudent.as_view()),
    url(r'^dashboard/studentlist/$', views.StudentListView.as_view(), name='studentlist'),
    url(r'^dashboard/students/(?P<pk>[0-9])+/$', views.StudentDetailView.as_view(), name='studentdetail'),
    url(r'^dashboard/students/(?P<pk>[0-9])+/edit$', views.StudentUpdateView.as_view(), name='studentedit'),
    url(r'^dashboard/teacherlist/$', views.TeacherListView.as_view()),
    url(r'^dashboard/teacherform/$', views.TeacherCreateView.as_view()),
    url(r'^dashboard/teachers/(?P<pk>[0-9])+/$', views.TeacherDetailView.as_view(), name='tacherdetail'),
    url(r'^dashboard/teachers/(?P<pk>[0-9])+/edit$', views.TeacherUpdateView.as_view(), name='teacheredit'),
    url(r'^dashboard/classroomlist/$', views.ClassroomListView.as_view()),
    url(r'^dashboard/classrooms/(?P<pk>[0-9])+/$', views.ClassroomDetailView.as_view(), name='classroomdetail'),
    url(r'^dashboard/classrooms/(?P<pk>[0-9])+/edit$', views.ClassroomUpdateView.as_view(), name='classroomedit'),
    url(r'^dashboard/teacherclasscourse/$', views.TeacherClassCourseCreateView.as_view(), name='teacherclasscourse'),
    url(r'^dashboard/studentregister/$', views.RegisterCreateView.as_view(), name='student_register'),
    url(r'students/api/$', views.student_list_api)
]
