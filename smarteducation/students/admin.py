from django.contrib import admin
from .models import Course, Subject, Student, StudentEnrollment, Exam, Result, AttendanceRecord, Feedback


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'credit_hours', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('teacher',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'course')
    search_fields = ('name', 'code')
    list_filter = ('course',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'section', 'status', 'attendance', 'marks', 'created_at')
    search_fields = ('name',)
    list_filter = ('status', 'grade', 'section')


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_date', 'status')
    list_filter = ('status', 'course')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'exam_type', 'total_marks', 'date')
    list_filter = ('exam_type', 'subject__course')
    search_fields = ('name',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade', 'created_at')
    list_filter = ('grade',)
    search_fields = ('student__name',)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status')
    list_filter = ('status', 'date', 'subject')
    search_fields = ('student__name',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'rating', 'created_at')
    list_filter = ('rating',)