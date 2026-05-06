from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db import models

from gym_app.models import UserProfile
from .models import Announcement


# ─────────────────────────────────────────────
# LIST ANNOUNCEMENTS (FOR ALL USERS)
# ─────────────────────────────────────────────

@login_required
def announcement_list(request):

    now = timezone.now()

    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        models.Q(expires_at__isnull=True) |
        models.Q(expires_at__gt=now)
    ).order_by('-created_at')

    profile = request.user.profile

    return render(request, 'announcements/list.html', {
        'announcements': announcements,
        'profile': profile
    })


# ─────────────────────────────────────────────
# CREATE ANNOUNCEMENT (OWNER ONLY)
# ─────────────────────────────────────────────

@login_required
def create_announcement(request):

    get_object_or_404(
        UserProfile,
        user=request.user,
        is_owner=True
    )

    if request.method == 'POST':

        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        priority = request.POST.get('priority', 'normal')
        expires_at_raw = request.POST.get('expires_at')

        if not title or not body:
            messages.error(request, 'Title and body are required.')
            return render(request, 'announcements/form.html', {
                'action': 'Create'
            })

        # ── HANDLE EXPIRATION ──
        expires_at = None

        if expires_at_raw:
            expires_at = parse_datetime(expires_at_raw)

            if expires_at and timezone.is_naive(expires_at):
                expires_at = timezone.make_aware(expires_at)

        Announcement.objects.create(
            title=title,
            body=body,
            priority=priority,
            expires_at=expires_at,
            created_by=request.user
        )

        messages.success(request, 'Announcement posted successfully!')
        return redirect('announcements')

    return render(request, 'announcements/form.html', {
        'action': 'Create'
    })
# ─────────────────────────────────────────────
# EDIT ANNOUNCEMENT (OWNER ONLY)
# ─────────────────────────────────────────────

@login_required
def edit_announcement(request, pk):

    get_object_or_404(
        UserProfile,
        user=request.user,
        is_owner=True
    )

    ann = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':

        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        priority = request.POST.get('priority', 'normal')
        is_active = request.POST.get('is_active') == 'on'
        expires_at_raw = request.POST.get('expires_at')

        if not title or not body:
            messages.error(request, "Title and body are required.")
            return render(request, 'announcements/form.html', {
                'ann': ann,
                'action': 'Edit'
            })

        # ── SAFE DATETIME HANDLING ──
        expires_at = None
        if expires_at_raw:
            expires_at = parse_datetime(expires_at_raw)

            # Only make aware if it's naive
            if expires_at and timezone.is_naive(expires_at):
                expires_at = timezone.make_aware(expires_at)

        # ── UPDATE FIELDS ──
        ann.title = title
        ann.body = body
        ann.priority = priority
        ann.is_active = True if request.POST.get('is_active') == 'on' else ann.is_active
        ann.expires_at = expires_at

        ann.save()

        messages.success(request, "Announcement updated successfully!")
        return redirect('announcements')

    return render(request, 'announcements/form.html', {
        'ann': ann,
        'action': 'Edit'
    })


# ─────────────────────────────────────────────
# DELETE ANNOUNCEMENT (OWNER ONLY)
# ─────────────────────────────────────────────

@login_required
def delete_announcement(request, pk):

    get_object_or_404(
        UserProfile,
        user=request.user,
        is_owner=True
    )

    ann = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        ann.delete()
        messages.success(request, 'Announcement deleted successfully.')

    return redirect('announcements')