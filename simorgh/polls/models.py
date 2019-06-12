from django.db import models
from edu.models import Teacher, Student, TeacherClassCourse

class Question(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    EXCELLENT, GOOD, MEDIUM, BAD = 'EX', 'GO', 'ME', 'BA'
    question_choices = (
        (EXCELLENT, 'عالی'),
        (GOOD, 'خوب'),
        (MEDIUM, 'متوسط'),
        (BAD, 'ضعیف')
    )
    choice_text = models.CharField(max_length=20, choices=question_choices)
    teacher_class_course = models.ForeignKey(TeacherClassCourse, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
