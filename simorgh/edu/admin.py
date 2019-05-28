from django.contrib import admin

from .models import Course, Teacher, Classroom, Student, LevelField, TeacherClassCourse, StudentCourse, Register, ClassTime

class TeacherAdmin(admin.ModelAdmin):
    # list_display = ('user', 'hire_date', 'profession')
    # list_filter = ('user', 'hire_date', 'profession')
    # search_fields = ('user__username', 'profession__name', 'user__first_name')
    pass


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Course)
admin.site.register(Classroom)
admin.site.register(Student)
admin.site.register(LevelField)
admin.site.register(TeacherClassCourse)
admin.site.register(StudentCourse)
admin.site.register(Register)
admin.site.register(ClassTime)


