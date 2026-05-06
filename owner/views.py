from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime, timedelta
import json

from gym_app.models import UserProfile, Payment, Attendance, WorkoutDay
from announcements.models import Announcement

# ── Pricing table ─────────────────────────────────────────────────────────────
PLAN_PRICES = {
    'daily':     60,
    'monthly':   500,
    'quarterly': 1_400,
    'annual':    5_000,
}

PLAN_DAYS = {
    'daily':     1,
    'monthly':   30,
    'quarterly': 90,
    'annual':    365,
}


@login_required
def owner_dashboard(request):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)

    today = date.today()

    # ── Stats ─────────────────────────────────────────────────────────────────
    total_members    = UserProfile.objects.filter(is_owner=False).count()
    present_today    = Attendance.objects.filter(date=today).count()
    paid_members     = Payment.objects.filter(status='paid').count()
    expired_count    = Payment.objects.filter(status='expired').count()
    pending_payments = Payment.objects.filter(status='pending').count()
    expiring_soon    = Payment.objects.filter(
        status='paid',
        expiry_date__lte=today + timedelta(days=7),
        expiry_date__gte=today,
    ).count()

    # ── Member rows ───────────────────────────────────────────────────────────
    members_qs = (
        User.objects
        .filter(profile__is_owner=False)
        .select_related('profile')
        .order_by('-date_joined')
    )
    member_rows = []
    for m in members_qs:
        latest_payment = Payment.objects.filter(user=m).order_by('-created_at').first()
        member_rows.append({
            'user':    m,
            'profile': m.profile,
            'payment': latest_payment,
        })

    # ── Today's attendance ────────────────────────────────────────────────────
    todays_attendance = (
        Attendance.objects
        .filter(date=today)
        .select_related('user', 'user__profile')
        .order_by('-time_in')
    )

    # ── Recent payments (all members, latest payment each) ────────────────────
    payments = (
        Payment.objects
        .select_related('user')
        .order_by('-created_at')[:20]
    )

    # ── Announcements ─────────────────────────────────────────────────────────
    announcements = (
        Announcement.objects
        .filter(is_active=True)
        .order_by('-created_at')[:5]
    )

    # ── 7-day trend chart ─────────────────────────────────────────────────────
    trend_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        trend_data.append({
            'date':  d.strftime('%a'),
            'count': Attendance.objects.filter(date=d).count(),
        })

    context = {
        # stats
        'total_members':    total_members,
        'present_today':    present_today,
        'paid_members':     paid_members,
        'expired_count':    expired_count,
        'pending_payments': pending_payments,
        'expiring_soon':    expiring_soon,
        # lists
        'member_rows':      member_rows,
        'todays_attendance': todays_attendance,
        'payments':         payments,
        'announcements':    announcements,
        # chart
        'trend_data':       json.dumps(trend_data),
        # misc
        'today':            today,
        'plan_prices':      PLAN_PRICES,
    }
    return render(request, 'owner/owner_dashboard.html', context)


@login_required
def member_detail(request, user_id):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)
    member         = get_object_or_404(User, id=user_id)
    member_profile = get_object_or_404(UserProfile, user=member)

    context = {
        'member':             member,
        'member_profile':     member_profile,
        'attendance_records': (
            Attendance.objects
            .filter(user=member)
            .order_by('-date', '-time_in')[:30]
        ),
        'payments': Payment.objects.filter(user=member).order_by('-created_at'),
        'workouts': WorkoutDay.objects.filter(user=member).prefetch_related('exercises'),
    }
    return render(request, 'owner/member_detail.html', context)


@login_required
def update_payment(request, user_id):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)
    member = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        status       = request.POST.get('status', 'pending')
        plan         = request.POST.get('plan', 'monthly')
        payment_date = request.POST.get('payment_date') or date.today().isoformat()
        expiry_date  = request.POST.get('expiry_date') or None

        payment, _created = Payment.objects.get_or_create(user=member)
        payment.status = status
        payment.plan   = plan
        payment.amount = PLAN_PRICES.get(plan, 0)

        pd = datetime.strptime(payment_date, '%Y-%m-%d').date()
        payment.payment_date = pd
        payment.expiry_date  = (
            datetime.strptime(expiry_date, '%Y-%m-%d').date()
            if expiry_date
            else pd + timedelta(days=PLAN_DAYS.get(plan, 30))
        )
        payment.save()

        # Sync UserProfile.membership_status
        profile = get_object_or_404(UserProfile, user=member)
        profile.membership_status = {
            'paid':    'active',
            'pending': 'pending',
        }.get(status, 'expired')
        profile.save()

        messages.success(
            request,
            f"✅ Payment updated for {member.get_full_name() or member.username} "
            f"— {plan.title()} plan (₱{PLAN_PRICES.get(plan, 0):,})"
        )
        return redirect('owner_dashboard')

    payment = Payment.objects.filter(user=member).first()
    context = {
        'member':      member,
        'payment':     payment,
        'plan_prices': PLAN_PRICES,
        'today':       date.today().isoformat(),
    }
    return render(request, 'owner/update_payment.html', context)


@login_required
def owner_attendance(request):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)
    today       = date.today()
    filter_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
    attendances = (
        Attendance.objects
        .filter(date=filter_date)
        .select_related('user')
        .order_by('-time_in')
    )
    context = {
        'attendances': attendances,
        'filter_date': filter_date,
        'today':       today.isoformat(),
    }
    return render(request, 'owner/owner_attendance.html', context)


@login_required
def owner_create_announcement(request):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        body     = request.POST.get('body', '').strip()
        priority = request.POST.get('priority', 'normal')
        expires  = request.POST.get('expires_at') or None
        if title and body:
            Announcement.objects.create(
                title=title, body=body, priority=priority,
                expires_at=expires, created_by=request.user,
            )
            messages.success(request, 'Announcement posted!')
        return redirect('owner_dashboard')
    return render(request, 'announcements/form.html', {'action': 'Create'})