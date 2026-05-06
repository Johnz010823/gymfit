from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import date
import json, base64, os, pickle
import numpy as np

from announcements.models import Announcement
from gym_app.models import UserProfile, WorkoutDay, WorkoutLog, Attendance
from attendance.views import _mark_attendance



# ── Home ───────────────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


# ── Member Dashboard ───────────────────────────────────────────────────────────
# ── Member Dashboard ───────────────────────────────────────────────────────────
# Replace your existing dashboard() function with this one.
# The only changes are: importing Payment and adding latest_payment to context.

@login_required
def dashboard(request):
    from datetime import timedelta
    # ← Add this import at the top of the file (or here if you prefer)
    from gym_app.models import Payment  # adjust app name if your Payment model lives elsewhere

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.is_owner:
        return redirect('owner_dashboard')

    today            = date.today()
    today_attendance = Attendance.objects.filter(user=request.user, date=today).first()
    week_start       = today - timedelta(days=today.weekday())
    weekly_logs      = WorkoutLog.objects.filter(user=request.user, date__gte=week_start).count()
    month_attendance = Attendance.objects.filter(
        user=request.user,
        date__month=today.month,
        date__year=today.year
    ).count()

    day_name        = today.strftime('%A')
    today_workout   = WorkoutDay.objects.filter(user=request.user, day=day_name).first()
    today_exercises = today_workout.exercises.all() if today_workout else []

    recent_attendance = Attendance.objects.filter(user=request.user)[:7]

    announcements = Announcement.objects.filter(
        is_active=True
    ).order_by('-created_at')[:3]

    # ── NEW: fetch the member's most recent payment ──────────────────────────
    latest_payment = (
        Payment.objects
        .filter(user=request.user)
        .order_by('-created_at')   # or '-date', '-paid_at' — use whichever field tracks when it was made
        .first()
    )
    # ────────────────────────────────────────────────────────────────────────

    chart_data = []
    for i in range(6, -1, -1):
        d     = today - timedelta(days=i)
        count = Attendance.objects.filter(user=request.user, date=d).count()
        chart_data.append({'date': d.strftime('%a'), 'present': 1 if count > 0 else 0})

    context = {
        'profile':           profile,
        'today_attendance':  today_attendance,
        'weekly_logs':       weekly_logs,
        'month_attendance':  month_attendance,
        'today_workout':     today_workout,
        'today_exercises':   today_exercises,
        'recent_attendance': recent_attendance,
        'chart_data':        json.dumps(chart_data),
        'day_name':          day_name,
        'announcements':     announcements,
        'latest_payment':    latest_payment,   # ← this was missing
    }
    return render(request, 'dashboard/member_dashboard.html', context)

# ── Owner Login ────────────────────────────────────────────────────────────────

def owner_login(request):
    if request.method == 'POST':
        email    = request.POST.get('login')
        password = request.POST.get('password')
        user     = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('owner_dashboard')
            return render(request, 'owner_login.html', {'error': 'You are not an owner.'})
        return render(request, 'owner_login.html', {'error': 'Invalid credentials.'})
    return render(request, 'owner_login.html')


# ── Face Registration ──────────────────────────────────────────────────────────

@login_required
def face_register(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'face/face_register.html', {'profile': profile})


@login_required
@csrf_exempt
def face_register_submit(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    try:
        data       = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({'success': False, 'error': 'No image data received'})
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        try:
            import face_recognition, cv2
            nparr   = np.frombuffer(image_bytes, np.uint8)
            img     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations:
                return JsonResponse({'success': False, 'error': 'No face detected.'})
            if len(face_locations) > 1:
                return JsonResponse({'success': False, 'error': 'Multiple faces detected.'})
            encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
            from django.conf import settings
            face_dir = settings.FACE_ENCODINGS_DIR
            os.makedirs(str(face_dir), exist_ok=True)
            encoding_path = os.path.join(str(face_dir), f'user_{request.user.id}.pkl')
            with open(encoding_path, 'wb') as f:
                pickle.dump(encoding, f)
            profile = request.user.profile
            profile.face_registered    = True
            profile.face_encoding_path = encoding_path
            profile.save()
            _mark_attendance(request.user, 'face')
            return JsonResponse({'success': True, 'message': 'Face registered successfully!'})
        except ImportError:
            profile = request.user.profile
            profile.face_registered    = True
            profile.face_encoding_path = f'demo_user_{request.user.id}'
            profile.save()
            _mark_attendance(request.user, 'face')
            return JsonResponse({'success': True, 'message': 'Face registered (demo mode).'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ── Face Login ─────────────────────────────────────────────────────────────────

def face_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'face/face_login.html')


@csrf_exempt
def face_login_verify(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    try:
        data       = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({'success': False, 'error': 'No image data'})
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        try:
            import face_recognition, cv2
            nparr   = np.frombuffer(image_bytes, np.uint8)
            img     = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations:
                return JsonResponse({'success': False, 'error': 'No face detected.'})
            if len(face_locations) > 1:
                return JsonResponse({'success': False, 'error': 'Multiple faces detected.'})
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            if not face_encodings:
                return JsonResponse({'success': False, 'error': 'Could not read face features.'})
            unknown_encoding = face_encodings[0]
            STRICT_THRESHOLD = 0.50
            registered_profiles = UserProfile.objects.filter(
                face_registered=True
            ).exclude(
                face_encoding_path__isnull=True
            ).exclude(
                face_encoding_path=''
            ).select_related('user')
            if not registered_profiles.exists():
                return JsonResponse({'success': False, 'error': 'No registered faces found.'})
            best_match_user = None
            best_distance   = STRICT_THRESHOLD
            for p in registered_profiles:
                enc_path = p.face_encoding_path
                if enc_path.startswith('demo_user_') or not os.path.exists(enc_path):
                    continue
                try:
                    with open(enc_path, 'rb') as f:
                        known_encoding = pickle.load(f)
                except (pickle.UnpicklingError, EOFError):
                    continue
                distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
                is_match = face_recognition.compare_faces(
                    [known_encoding], unknown_encoding, tolerance=STRICT_THRESHOLD
                )[0]
                if is_match and distance < best_distance:
                    best_distance   = distance
                    best_match_user = p.user
            if best_match_user:
                login(request, best_match_user,
                      backend='django.contrib.auth.backends.ModelBackend')
                _mark_attendance(best_match_user, 'face')
                return JsonResponse({
                    'success':    True,
                    'redirect':   '/dashboard/',
                    'name':       best_match_user.get_full_name() or best_match_user.username,
                    'confidence': round((1 - best_distance) * 100, 1),
                })
            return JsonResponse({'success': False, 'error': 'Face not recognized.'})
        except ImportError:
            return JsonResponse({'success': False, 'error': 'face_recognition not installed.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ── Profile & Logout ───────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name  = request.POST.get('last_name', '')
        request.user.save()
        profile.phone   = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'dashboard/profile.html', {'profile': profile})


def custom_logout(request):
    logout(request)
    messages.info(request, '')
    return redirect('home')


def exercise_viewer(request, day=None):
    return render(request, 'exercise_viewer.html', {'day': day})