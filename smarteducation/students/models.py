from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    credit_hours = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=20, blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    attendance = models.FloatField(default=0)
    marks = models.FloatField(default=0)
    report = models.FileField(upload_to='reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentEnrollment(models.Model):
    ENROLLMENT_STATUS = (
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ENROLLMENT_STATUS, default='enrolled')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} - {self.course.code}"


class Exam(models.Model):
    EXAM_TYPES = (
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )

    name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    total_marks = models.FloatField(default=100)
    date = models.DateField()
    exam_type = models.CharField(max_length=15, choices=EXAM_TYPES, default='midterm')

    def __str__(self):
        return f"{self.name} ({self.exam_type})"


class Result(models.Model):
    GRADE_CHOICES = (
        ('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B'),
        ('C+', 'C+'), ('C', 'C'), ('D', 'D'), ('F', 'F'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.FloatField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {self.marks_obtained}"

    def save(self, *args, **kwargs):
        if not self.grade:
            percentage = (self.marks_obtained / self.exam.total_marks) * 100
            if percentage >= 90:
                self.grade = 'A+'
            elif percentage >= 80:
                self.grade = 'A'
            elif percentage >= 70:
                self.grade = 'B+'
            elif percentage >= 60:
                self.grade = 'B'
            elif percentage >= 50:
                self.grade = 'C+'
            elif percentage >= 40:
                self.grade = 'C'
            elif percentage >= 30:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)


class AttendanceRecord(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default='present')

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.name} - {self.date}: {self.status}"


class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='given_feedback')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} -> {self.teacher.username}: {self.rating}/5"