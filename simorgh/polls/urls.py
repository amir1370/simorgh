from . import views
from django.conf.urls import url

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.TeacherClassCourseListView.as_view(), name='teacher_course_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.ChoiceCreateView.as_view(), name='choice_form'),
]
