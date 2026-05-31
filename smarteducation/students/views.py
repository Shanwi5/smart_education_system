from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .models import Student, Course, Subject, Exam, Result, AttendanceRecord, StudentEnrollment, Feedback


@login_required
def home(request):
    """Student list with search and filter."""
    students = Student.objects.all()

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(grade__icontains=search_query) |
            Q(section__icontains=search_query)
        )

    # Filters
    grade_filter = request.GET.get('grade', '')
    if grade_filter:
        students = students.filter(grade=grade_filter)

    status_filter = request.GET.get('status', '')
    if status_filter:
        students = students.filter(status=status_filter)

    attendance_min = request.GET.get('attendance_min', '')
    if attendance_min:
        students = students.filter(attendance__gte=float(attendance_min))

    marks_min = request.GET.get('marks_min', '')
    if marks_min:
        students = students.filter(marks__gte=float(marks_min))

    context = {
        'students': students,
        'search_query': search_query,
        'grade_filter': grade_filter,
        'status_filter': status_filter,
    }
    return render(request, 'students/student_list.html', context)


@login_required
def student_create(request):
    """Add a new student."""
    if request.method == 'POST':
        name = request.POST['name']
        grade = request.POST.get('grade', '')
        section = request.POST.get('section', '')
        attendance = request.POST.get('attendance', 0)
        marks = request.POST.get('marks', 0)
        report = request.FILES.get('report')

        Student.objects.create(
            name=name,
            grade=grade or None,
            section=section or None,
            attendance=attendance,
            marks=marks,
            report=report
        )
        return redirect('student_list')

    return render(request, 'students/student_form.html')


@login_required
def student_detail(request, pk):
    """View student details."""
    student = get_object_or_404(Student, pk=pk)
    results = Result.objects.filter(student=student)
    attendance_records = AttendanceRecord.objects.filter(student=student)[:20]
    enrollments = StudentEnrollment.objects.filter(student=student)
    feedback_given = Feedback.objects.filter(student=student)

    context = {
        'student': student,
        'results': results,
        'attendance_records': attendance_records,
        'enrollments': enrollments,
        'feedback_given': feedback_given,
    }
    return render(request, 'students/student_detail.html', context)


@login_required
def student_update(request, pk):
    """Update student record."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.name = request.POST.get('name', student.name)
        student.grade = request.POST.get('grade', student.grade)
        student.section = request.POST.get('section', student.section)
        student.attendance = request.POST.get('attendance', student.attendance)
        student.marks = request.POST.get('marks', student.marks)
        student.status = request.POST.get('status', student.status)
        if 'report' in request.FILES:
            student.report = request.FILES['report']
        student.save()
        return redirect('student_detail', pk=student.pk)

    context = {'student': student}
    return render(request, 'students/student_form.html', context)


@login_required
def student_delete(request, pk):
    """Delete student record."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    context = {'student': student}
    return render(request, 'students/student_confirm_delete.html', context)


# Course views
@login_required
def course_list(request):
    courses = Course.objects.all()
    search_query = request.GET.get('q', '')
    if search_query:
        courses = courses.filter(Q(name__icontains=search_query) | Q(code__icontains=search_query))
    return render(request, 'students/course_list.html', {'courses': courses, 'search_query': search_query})


@login_required
def course_create(request):
    if request.method == 'POST':
        Course.objects.create(
            name=request.POST['name'],
            code=request.POST['code'],
            description=request.POST.get('description', ''),
            teacher=request.user if request.user.profile.role == 'teacher' else None,
            credit_hours=request.POST.get('credit_hours', 3),
        )
        return redirect('course_list')
    return render(request, 'students/course_form.html')


# Exam views
@login_required
def exam_list(request):
    exams = Exam.objects.select_related('subject').all()
    return render(request, 'students/exam_list.html', {'exams': exams})


@login_required
def exam_create(request):
    if request.method == 'POST':
        Exam.objects.create(
            name=request.POST['name'],
            subject_id=request.POST['subject'],
            total_marks=request.POST.get('total_marks', 100),
            date=request.POST['date'],
            exam_type=request.POST.get('exam_type', 'midterm'),
        )
        return redirect('exam_list')
    subjects = Subject.objects.all()
    return render(request, 'students/exam_form.html', {'subjects': subjects})


# Result views
@login_required
def result_list(request):
    results = Result.objects.select_related('student', 'exam').all()
    search_query = request.GET.get('q', '')
    if search_query:
        results = results.filter(student__name__icontains=search_query)

    grade_filter = request.GET.get('grade', '')
    if grade_filter:
        results = results.filter(grade=grade_filter)

    return render(request, 'students/result_list.html', {
        'results': results,
        'search_query': search_query,
    })


@login_required
def result_create(request):
    if request.method == 'POST':
        Result.objects.create(
            student_id=request.POST['student'],
            exam_id=request.POST['exam'],
            marks_obtained=request.POST['marks_obtained'],
            remarks=request.POST.get('remarks', ''),
        )
        return redirect('result_list')
    students = Student.objects.filter(status='active')
    exams = Exam.objects.all()
    return render(request, 'students/result_form.html', {'students': students, 'exams': exams})


# Attendance views
@login_required
def attendance_list(request):
    records = AttendanceRecord.objects.select_related('student', 'subject').all()
    search_query = request.GET.get('q', '')
    if search_query:
        records = records.filter(student__name__icontains=search_query)

    status_filter = request.GET.get('status', '')
    if status_filter:
        records = records.filter(status=status_filter)

    return render(request, 'students/attendance_list.html', {
        'records': records,
        'search_query': search_query,
    })


@login_required
def attendance_create(request):
    if request.method == 'POST':
        AttendanceRecord.objects.create(
            student_id=request.POST['student'],
            subject_id=request.POST['subject'],
            date=request.POST['date'],
            status=request.POST['status'],
        )
        return redirect('attendance_list')
    students = Student.objects.filter(status='active')
    subjects = Subject.objects.all()
    return render(request, 'students/attendance_form.html', {'students': students, 'subjects': subjects})


# Feedback views
@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.select_related('student', 'teacher').all()
    return render(request, 'students/feedback_list.html', {'feedbacks': feedbacks})


@login_required
def feedback_create(request):
    if request.method == 'POST':
        student = Student.objects.get(pk=request.POST['student'])
        Feedback.objects.create(
            student=student,
            teacher_id=request.POST['teacher'],
            rating=request.POST['rating'],
            comment=request.POST.get('comment', ''),
        )
        return redirect('feedback_list')
    students = Student.objects.filter(status='active')
    from django.contrib.auth.models import User
    teachers = User.objects.filter(profile__role='teacher')
    return render(request, 'students/feedback_form.html', {'students': students, 'teachers': teachers})