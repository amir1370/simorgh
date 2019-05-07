from django.conf.urls import url
from edu import views

app_name = 'edu'
urlpatterns = [
    url(r'^(?P<class_id>[0-9])+/$', views.class_list),
    url(r'^home/studentform/$', views.FormViewStudent.as_view()),
    url(r'^home/studentlist/$', views.StudentListView.as_view()),
    url(r'^home/students/(?P<pk>[0-9])+/$', views.StudentDetailView.as_view(), name='studentdetail'),
    url(r'^home/students/(?P<pk>[0-9])+/edit$', views.StudentUpdateView.as_view(), name='studentedit'),
    url(r'^home/teacherlist/$', views.TeacherListView.as_view()),
    url(r'^home/teachers/(?P<pk>[0-9])+/$', views.TeacherDetailView.as_view(), name='tacherdetail'),
    url(r'^home/teachers/(?P<pk>[0-9])+/edit$', views.TeacherUpdateView.as_view(), name='teacheredit'),
    url(r'^home/classroomlist/$', views.ClassroomListView.as_view()),
    url(r'^home/classrooms/(?P<pk>[0-9])+/$', views.ClassroomDetailView.as_view(), name='classroomdetail'),
    url(r'^home/classrooms/(?P<pk>[0-9])+/edit$', views.ClassroomUpdateView.as_view(), name='classroomedit'),
]
