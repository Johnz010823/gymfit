from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date

from gym_app.models import Attendance, UserProfile


# ─── Shared helper ────────────────────────────────────────────────────────────

def _mark_attendance(user, method='credentials'):
    """
    Creates a new attendance record for today if one doesn't exist yet.
    Returns the existing record (or None if it was just created).
    `method` should be 'credentials' or 'face'.
    """
    today    = date.today()
    existing = Attendance.objects.filter(user=user, date=today).first()
    if not existing:
        local_now = timezone.localtime(timezone.now())   # UTC → Asia/Manila
        Attendance.objects.create(
            user=user,
            date=today,
            time_in=local_now.time(),
            login_method=method,
        )
        return None   # freshly created
    return existing   # already had a record


# ─── Views ───────────────────────────────────────────────────────────────────

@login_required
def attendance_list(request):
    profile     = request.user.profile
    attendances = Attendance.objects.filter(user=request.user).order_by('-date')
    today       = date.today()
    monthly     = Attendance.objects.filter(
        user=request.user,
        date__month=today.month,
        date__year=today.year,
    ).values('date').distinct().count()

    context = {
        'attendances':   attendances,
        'monthly_count': monthly,
        'profile':       profile,
    }
    return render(request, 'dashboard/attendance.html', context)


@login_required
def mark_checkout(request):
    today      = timezone.localdate()
    attendance = Attendance.objects.filter(user=request.user, date=today).first()
    if attendance and not attendance.time_out:
        attendance.time_out = timezone.localtime(timezone.now()).time()
        attendance.save()
        messages.success(request, 'Checkout recorded successfully!')
    return redirect('dashboard')