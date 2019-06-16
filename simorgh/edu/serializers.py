from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Student, Course, StudentCourse


class CourseSerializer(serializers.Serializer):
    name = serializers.CharField()
    unit = serializers.IntegerField()

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()

class StudentSerializer(serializers.Serializer):
    user = UserSerializer()
    courses = CourseSerializer(many=True)
    student_id = serializers.IntegerField()
    last_modified_date = serializers.DateTimeField()

    def create(self, validated_data):
        course_data = {}
        course_data['name'] = validated_data.pop('name')
        course_data['unit'] = validated_data.pop('unit')
        new_course = Course.objects.create(**course_data)
        user_data = {}
        user_data['username'] = validated_data.pop('username')
        user_data['password'] = make_password(validated_data.pop('password'))
        user_data['email'] = make_password(validated_data.pop('email'))
        new_user=User.objects.create(**user_data)
        return Student.objects.create(user=new_user, courses = new_course**validated_data)


class StudentCourseSerializer(serializers.Serializer):
    course = serializers.CharField()
    student = serializers.CharField()
    mid_grade = serializers.FloatField()
    final_grade = serializers.FloatField()
    # teacher = serializers.CharField()
    # class Meta:
    #     model = StudentCourse
    #     fields = '__all__'