from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate  # ✅ added authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count, Q
import json
import base64
import os
import pickle
import numpy as np
from datetime import date, timedelta
import io
from .models import (
    UserProfile, Payment, WorkoutDay, Exercise,
    WorkoutLog, Attendance
)

# ─── Full Exercise Library ─────────────────────────────────────────────────────

EXERCISE_LIBRARY = {
    'Chest': {
        'icon': '🏋️',
        'color': 'danger',
        'subcategories': {
            'Compound': [
                'Bench Press (Barbell)', 'Bench Press (Dumbbell)',
                'Incline Bench Press', 'Decline Bench Press',
                'Chest Press Machine', 'Dips', 'Push-ups',
                'Incline Dumbbell Press',
            ],
            'Isolation': [
                'Cable Flyes', 'Pec Deck Machine',
                'Dumbbell Flyes', 'Cable Crossover',
            ],
        },
    },
    'Back': {
        'icon': '🦾',
        'color': 'primary',
        'subcategories': {
            'Vertical Pull': [
                'Pull-ups', 'Chin-ups',
                'Lat Pulldown (Wide Grip)', 'Lat Pulldown (Narrow Grip)',
            ],
            'Rows': [
                'Barbell Row', 'One-Arm Dumbbell Row',
                'Seated Cable Row', 'T-Bar Row', 'Chest-Supported Row',
            ],
            'Lower Back & Traps': [
                'Deadlift', 'Rack Pulls',
                'Barbell Shrugs', 'Hyperextensions',
            ],
        },
    },
    'Shoulders': {
        'icon': '💪',
        'color': 'warning',
        'subcategories': {
            'Pressing': [
                'Overhead Press (Military Press)', 'Arnold Press',
                'Seated Dumbbell Press', 'Push Press',
            ],
            'Raises & Isolation': [
                'Lateral Raise', 'Front Raise',
                'Face Pulls', 'Reverse Pec Deck', 'Rear Delt Fly',
            ],
        },
    },
    'Legs': {
        'icon': '🦵',
        'color': 'success',
        'subcategories': {
            'Quads': [
                'Barbell Squat (Back)', 'Barbell Squat (Front)',
                'Leg Press', 'Hack Squat', 'Leg Extensions',
                'Bulgarian Split Squats', 'Lunges',
            ],
            'Hamstrings & Glutes': [
                'Romanian Deadlift (RDL)', 'Stiff-Leg Deadlift',
                'Leg Curls (Lying)', 'Leg Curls (Seated)',
                'Hip Thrusts', 'Glute Bridges', 'Kettlebell Swings',
            ],
            'Calves': [
                'Standing Calf Raise',
                'Seated Calf Raise',
                'Donkey Calf Raise',
            ],
        },
    },
    'Arms': {
        'icon': '💪',
        'color': 'info',
        'subcategories': {
            'Biceps': [
                'Barbell Curl', 'Dumbbell Curl', 'Hammer Curl',
                'Preacher Curl', 'Concentration Curl', '21s',
            ],
            'Triceps': [
                'Triceps Pushdown (Rope)', 'Triceps Pushdown (Bar)',
                'Skull Crushers', 'Close-Grip Bench Press',
                'Overhead Triceps Extension', 'Tricep Dips', 'Kickbacks',
            ],
        },
    },
    'Core': {
        'icon': '🔥',
        'color': 'secondary',
        'subcategories': {
            'Stability': [
                'Plank', 'Side Plank', 'Bird-Dog', 'Dead Bug',
            ],
            'Flexion & Rotation': [
                'Hanging Leg Raise', 'Russian Twists',
                'Cable Woodchoppers', 'Ab Wheel Rollouts', 'Crunches',
            ],
        },
    },
    'Full Body & Cardio': {
        'icon': '🏃',
        'color': 'dark',
        'subcategories': {
            'Full Body': [
                'Clean and Jerk', 'Snatch', 'Burpees', 'Thrusters',
            ],
            'Cardio': [
                'Treadmill Run', 'Elliptical', 'Stairmaster',
                'Stationary Bike', 'Rowing Machine', 'Battle Ropes',
            ],
        },
    },
}

# Default sets/reps per category
DEFAULT_PARAMS = {
    'Chest':              (3, 10),
    'Back':               (4, 10),
    'Shoulders':          (3, 12),
    'Legs':               (4, 10),
    'Arms':               (3, 12),
    'Core':               (3, 30),
    'Full Body & Cardio': (3, 10),
}

# ─── Home ─────────────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.is_owner:
        return redirect('owner_dashboard')

    today = date.today()
    today_attendance = Attendance.objects.filter(user=request.user, date=today).first()
    week_start = today - timedelta(days=today.weekday())
    weekly_logs = WorkoutLog.objects.filter(user=request.user, date__gte=week_start).count()
    month_attendance = Attendance.objects.filter(
        user=request.user, date__month=today.month, date__year=today.year
    ).count()
    day_name = today.strftime('%A')
    today_workout = WorkoutDay.objects.filter(user=request.user, day=day_name).first()
    today_exercises = today_workout.exercises.all() if today_workout else []
    latest_payment = Payment.objects.filter(user=request.user).first()
    recent_attendance = Attendance.objects.filter(user=request.user)[:7]
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        count = Attendance.objects.filter(user=request.user, date=d).count()
        chart_data.append({'date': d.strftime('%a'), 'present': 1 if count > 0 else 0})
    context = {
        'profile': profile,
        'today_attendance': today_attendance,
        'weekly_logs': weekly_logs,
        'month_attendance': month_attendance,
        'today_workout': today_workout,
        'today_exercises': today_exercises,
        'latest_payment': latest_payment,
        'recent_attendance': recent_attendance,
        'chart_data': json.dumps(chart_data),
        'day_name': day_name,
    }
    return render(request, 'dashboard/member_dashboard.html', context)


# ─── Owner Login ───────────────────────────────────────────────────────────────

def owner_login(request):
    if request.method == "POST":
        email = request.POST.get("login")
        password = request.POST.get("password")

        # ✅ authenticate is now properly imported
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('owner_dashboard')
            else:
                return render(
                    request,
                    'owner_login.html',
                    {'error': 'You are not an owner'}
                )
        else:
            return render(
                request,
                'owner_login.html',
                {'error': 'Invalid credentials'}  # ✅ handle failed login
            )

    return render(request, 'owner_login.html')


# ─── Face Registration ─────────────────────────────────────────────────────────

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
        data = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({'success': False, 'error': 'No image data received'})
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        try:
            import face_recognition
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations:
                return JsonResponse({'success': False, 'error': 'No face detected. Please ensure your face is clearly visible.'})
            if len(face_locations) > 1:
                return JsonResponse({'success': False, 'error': 'Multiple faces detected. Please ensure only your face is in frame.'})
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            encoding = face_encodings[0]
            from django.conf import settings
            face_dir = settings.FACE_ENCODINGS_DIR
            os.makedirs(str(face_dir), exist_ok=True)
            encoding_path = os.path.join(str(face_dir), f'user_{request.user.id}.pkl')
            with open(encoding_path, 'wb') as f:
                pickle.dump(encoding, f)
            profile = request.user.profile
            profile.face_registered = True
            profile.face_encoding_path = encoding_path
            profile.save()
            _mark_attendance(request.user, 'face')
            return JsonResponse({'success': True, 'message': 'Face registered successfully! You can now use face login.'})
        except ImportError:
            profile = request.user.profile
            profile.face_registered = True
            profile.face_encoding_path = f'demo_user_{request.user.id}'
            profile.save()
            _mark_attendance(request.user, 'face')
            return JsonResponse({'success': True, 'message': 'Face registered (demo mode). Install face_recognition for full functionality.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── Face Login ────────────────────────────────────────────────────────────────

def face_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'face/face_login.html')


@csrf_exempt
def face_login_verify(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({'success': False, 'error': 'No image data'})
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        try:
            import face_recognition
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations:
                return JsonResponse({'success': False, 'error': 'No face detected. Please look directly at the camera.'})
            if len(face_locations) > 1:
                return JsonResponse({'success': False, 'error': 'Multiple faces detected. Please ensure only you are in frame.'})
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            if not face_encodings:
                return JsonResponse({'success': False, 'error': 'Could not read face features. Try again with better lighting.'})
            unknown_encoding = face_encodings[0]
            STRICT_THRESHOLD = 0.50
            registered_profiles = UserProfile.objects.filter(face_registered=True).exclude(
                face_encoding_path__isnull=True).exclude(face_encoding_path='').select_related('user')
            if not registered_profiles.exists():
                return JsonResponse({'success': False, 'error': 'No registered faces found. Please register your face first.'})
            best_match_user = None
            best_distance = STRICT_THRESHOLD
            for profile in registered_profiles:
                enc_path = profile.face_encoding_path
                if enc_path.startswith('demo_user_'):
                    continue
                if not os.path.exists(enc_path):
                    profile.face_registered = False
                    profile.face_encoding_path = ''
                    profile.save()
                    continue
                try:
                    with open(enc_path, 'rb') as f:
                        known_encoding = pickle.load(f)
                except (pickle.UnpicklingError, EOFError):
                    continue
                distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
                is_match = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=STRICT_THRESHOLD)[0]
                if is_match and distance < best_distance:
                    best_distance = distance
                    best_match_user = profile.user
            if best_match_user is not None:
                login(request, best_match_user, backend='django.contrib.auth.backends.ModelBackend')
                _mark_attendance(best_match_user, 'face')
                return JsonResponse({
                    'success': True,
                    'redirect': '/dashboard/',
                    'name': best_match_user.get_full_name() or best_match_user.username,
                    'confidence': round((1 - best_distance) * 100, 1),
                })
            else:
                return JsonResponse({'success': False, 'error': 'Face not recognized. Please register your face first, or use Google login.'})
        except ImportError:
            return JsonResponse({'success': False, 'error': 'Face recognition library is not installed. Please use Google login or ask your admin to install face_recognition.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'})


# ─── Attendance ────────────────────────────────────────────────────────────────

def _mark_attendance(user, method='face'):
    today = date.today()
    existing = Attendance.objects.filter(user=user, date=today).first()
    if not existing:
        local_now = timezone.localtime(timezone.now())
        Attendance.objects.create(
            user=user,
            date=today,
            time_in=local_now.time(),
            login_method=method,
        )
    return existing


@login_required  # ✅ removed duplicate @login_required
def attendance_list(request):
    profile = request.user.profile
    attendances = Attendance.objects.filter(
        user=request.user
    ).order_by('-date')
    today = date.today()
    monthly = Attendance.objects.filter(
        user=request.user,
        date__month=today.month,
        date__year=today.year
    ).values('date').distinct().count()
    context = {
        'attendances': attendances,
        'monthly_count': monthly,
        'profile': profile,
    }
    return render(request, 'dashboard/attendance.html', context)


@login_required
def mark_checkout(request):
    today = timezone.localdate()
    attendance = Attendance.objects.filter(user=request.user, date=today).first()
    if attendance and not attendance.time_out:
        attendance.time_out = timezone.localtime(timezone.now()).time()
        attendance.save()
        messages.success(request, 'Checkout recorded successfully!')
    return redirect('dashboard')


# ─── Workout ────────────────────────────────────────────────────────────────────

@login_required
def workout_plan(request):
    profile = request.user.profile
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    workout_days = [
        (day, WorkoutDay.objects.filter(user=request.user, day=day).prefetch_related('exercises').first())
        for day in days
    ]
    context = {
        'workout_days': workout_days,
        'profile': profile,
        'today_name': date.today().strftime('%A'),
        'exercise_library': EXERCISE_LIBRARY,
    }
    return render(request, 'workouts/workout_plan.html', context)


@login_required
@csrf_exempt
def toggle_exercise(request, exercise_id):
    if request.method == 'POST':
        exercise = get_object_or_404(Exercise, id=exercise_id, workout_day__user=request.user)
        exercise.is_completed = not exercise.is_completed
        if exercise.is_completed:
            exercise.completed_at = timezone.now()
            WorkoutLog.objects.create(
                user=request.user, exercise=exercise, exercise_name=exercise.name,
                sets_completed=exercise.sets, reps_completed=exercise.reps,
                weight_kg=exercise.weight_kg,
            )
        else:
            exercise.completed_at = None
        exercise.save()
        return JsonResponse({'success': True, 'completed': exercise.is_completed})
    return JsonResponse({'success': False})


@login_required
def toggle_rest_day(request, day):
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if day not in valid_days:
        messages.error(request, 'Invalid day.')
        return redirect('workout_plan')
    workout_day, created = WorkoutDay.objects.get_or_create(
        user=request.user, day=day,
        defaults={'muscle_group': '', 'is_rest_day': True}
    )
    if not created:
        workout_day.is_rest_day = not workout_day.is_rest_day
        workout_day.save()
        status = 'rest day' if workout_day.is_rest_day else 'training day'
        messages.success(request, f'{day} is now a {status}.')
    else:
        messages.success(request, f'{day} has been set as a rest day.')
    return redirect('workout_plan')


@login_required
def exercise_library_view(request, day):
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if day not in valid_days:
        messages.error(request, 'Invalid day.')
        return redirect('workout_plan')
    workout_day, _ = WorkoutDay.objects.get_or_create(
        user=request.user, day=day,
        defaults={'muscle_group': day, 'is_rest_day': False}
    )
    if workout_day.is_rest_day:
        workout_day.is_rest_day = False
        workout_day.save()
    existing_exercise_names = list(
        workout_day.exercises.values_list('name', flat=True)
    )
    context = {
        'day': day,
        'workout_day': workout_day,
        'exercise_library': EXERCISE_LIBRARY,
        'existing_exercises': existing_exercise_names,
    }
    return render(request, 'workouts/exercise_library.html', context)


@login_required
def add_from_library(request, day):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if day not in valid_days:
        return JsonResponse({'success': False, 'error': 'Invalid day'})
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    exercises_data = data.get('exercises', [])
    muscle_group   = data.get('muscle_group', '')
    if not exercises_data:
        return JsonResponse({'success': False, 'error': 'No exercises selected'})
    workout_day, _ = WorkoutDay.objects.get_or_create(
        user=request.user, day=day,
        defaults={'muscle_group': muscle_group or day, 'is_rest_day': False}
    )
    if muscle_group:
        workout_day.muscle_group = muscle_group
    workout_day.is_rest_day = False
    workout_day.save()
    added = []
    skipped = []
    for ex in exercises_data:
        name = ex.get('name', '').strip()
        if not name:
            continue
        sets      = int(ex.get('sets', 3))
        reps      = int(ex.get('reps', 10))
        weight    = ex.get('weight', '') or None
        weight_kg = float(weight) if weight else None
        obj, created = Exercise.objects.get_or_create(
            workout_day=workout_day,
            name=name,
            defaults={'sets': sets, 'reps': reps, 'weight_kg': weight_kg}
        )
        if created:
            added.append(name)
        else:
            skipped.append(name)
    msg_parts = []
    if added:
        msg_parts.append(f'{len(added)} exercise(s) added')
    if skipped:
        msg_parts.append(f'{len(skipped)} already existed')
    return JsonResponse({
        'success': True,
        'message': ', '.join(msg_parts) + f' for {day}.',
        'added': added,
        'skipped': skipped,
    })


@login_required
def suggest_workout(request):
    suggestions = {
        'Monday': {
            'muscle_group': 'Chest & Triceps',
            'exercises': [
                ('Bench Press (Barbell)', 4, 10),
                ('Incline Dumbbell Press', 3, 12),
                ('Cable Flyes', 3, 15),
                ('Triceps Pushdown (Rope)', 3, 12),
                ('Skull Crushers', 3, 10),
            ],
        },
        'Tuesday': {
            'muscle_group': 'Back & Biceps',
            'exercises': [
                ('Pull-ups', 4, 8),
                ('Barbell Row', 4, 10),
                ('Seated Cable Row', 3, 12),
                ('Lat Pulldown (Wide Grip)', 3, 12),
                ('Barbell Curl', 3, 12),
                ('Hammer Curl', 3, 12),
            ],
        },
        'Wednesday': {
            'muscle_group': 'Legs',
            'exercises': [
                ('Barbell Squat (Back)', 4, 10),
                ('Leg Press', 4, 12),
                ('Romanian Deadlift (RDL)', 3, 10),
                ('Leg Extensions', 3, 12),
                ('Leg Curls (Lying)', 3, 12),
                ('Standing Calf Raise', 4, 15),
            ],
        },
        'Thursday': {
            'muscle_group': 'Shoulders & Core',
            'exercises': [
                ('Overhead Press (Military Press)', 4, 10),
                ('Lateral Raise', 4, 15),
                ('Front Raise', 3, 12),
                ('Face Pulls', 3, 15),
                ('Plank', 3, 60),
                ('Hanging Leg Raise', 3, 12),
            ],
        },
        'Friday': {
            'muscle_group': 'Arms',
            'exercises': [
                ('Barbell Curl', 3, 12),
                ('Hammer Curl', 3, 12),
                ('Preacher Curl', 3, 10),
                ('Triceps Pushdown (Rope)', 3, 12),
                ('Skull Crushers', 3, 10),
                ('Overhead Triceps Extension', 3, 12),
            ],
        },
        'Saturday': {
            'muscle_group': 'Full Body & Cardio',
            'exercises': [
                ('Deadlift', 3, 8),
                ('Barbell Squat (Back)', 3, 8),
                ('Push-ups', 3, 20),
                ('Pull-ups', 3, 8),
                ('Burpees', 3, 10),
                ('Plank', 3, 60),
            ],
        },
        'Sunday': None,
    }
    today_name = date.today().strftime('%A')
    plan = suggestions.get(today_name)
    if plan is None:
        messages.info(request, '😴 Today is a rest day. Recovery is part of training!')
        return redirect('workout_plan')
    muscle_group = plan['muscle_group']
    exercises    = plan['exercises']
    workout_day, created = WorkoutDay.objects.get_or_create(
        user=request.user, day=today_name,
        defaults={'muscle_group': muscle_group, 'is_rest_day': False}
    )
    if not created:
        workout_day.muscle_group = muscle_group
        workout_day.is_rest_day  = False
        workout_day.save()
    added_count = 0
    for name, sets, reps in exercises:
        _, ex_created = Exercise.objects.get_or_create(
            workout_day=workout_day,
            name=name,
            defaults={'sets': sets, 'reps': reps}
        )
        if ex_created:
            added_count += 1
    if added_count:
        messages.success(request, f'✅ {muscle_group} workout suggested for {today_name}! ({added_count} exercises added)')
    else:
        messages.info(request, f'ℹ️ You already have a {muscle_group} plan for {today_name}.')
    return redirect('workout_plan')


@login_required
def add_exercise(request, day):
    workout_day, _ = WorkoutDay.objects.get_or_create(
        user=request.user, day=day,
        defaults={'muscle_group': day, 'is_rest_day': False}
    )
    if request.method == 'POST':
        name   = request.POST.get('name', '').strip()
        sets   = request.POST.get('sets', 3)
        reps   = request.POST.get('reps', 10)
        weight = request.POST.get('weight', '')
        if not name:
            messages.error(request, 'Exercise name is required.')
            return render(request, 'workouts/add_exercise.html', {'day': day})
        Exercise.objects.create(
            workout_day=workout_day, name=name,
            sets=int(sets), reps=int(reps),
            weight_kg=float(weight) if weight else None
        )
        messages.success(request, f'"{name}" added to {day}!')
        return redirect('workout_plan')
    return render(request, 'workouts/add_exercise.html', {'day': day})


@login_required
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, workout_day__user=request.user)
    if request.method == 'POST':
        name   = request.POST.get('name', '').strip()
        sets   = request.POST.get('sets', exercise.sets)
        reps   = request.POST.get('reps', exercise.reps)
        weight = request.POST.get('weight', '')
        if not name:
            messages.error(request, 'Exercise name is required.')
            return render(request, 'workouts/edit_exercise.html', {'exercise': exercise})
        exercise.name      = name
        exercise.sets      = int(sets)
        exercise.reps      = int(reps)
        exercise.weight_kg = float(weight) if weight else None
        exercise.save()
        messages.success(request, f'"{name}" updated!')
        return redirect('workout_plan')
    return render(request, 'workouts/edit_exercise.html', {'exercise': exercise})


@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, workout_day__user=request.user)
    if request.method == 'POST':
        name = exercise.name
        exercise.delete()
        messages.success(request, f'"{name}" removed.')
    return redirect('workout_plan')


# ─── Owner Dashboard ───────────────────────────────────────────────────────────

@login_required
def owner_dashboard(request):

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user
    )

    # Check if owner
    if not profile.is_owner:
        messages.error(request, "You are not authorized as owner.")
        return redirect('dashboard')

    members = UserProfile.objects.filter(
        is_owner=False
    ).select_related('user')

    today = date.today()

    present_today = Attendance.objects.filter(
        date=today
    ).values('user').distinct().count()

    paid_members = Payment.objects.filter(
        status='paid'
    ).values('user').distinct().count()

    expired = Payment.objects.filter(
        expiry_date__lt=today,
        status='paid'
    ).count()

    recent_attendance = Attendance.objects.select_related('user')[:20]

    payments = Payment.objects.select_related(
        'user'
    ).order_by('-created_at')[:20]

    trend = [
        {
            'date': (today - timedelta(days=i)).strftime('%b %d'),
            'count': Attendance.objects.filter(
                date=today - timedelta(days=i)
            ).values('user').distinct().count()
        }
        for i in range(6, -1, -1)
    ]

    context = {
        'profile': profile,
        'members': members,
        'total_members': members.count(),
        'present_today': present_today,
        'paid_members': paid_members,
        'expired_count': expired,
        'recent_attendance': recent_attendance,
        'payments': payments,
        'trend_data': json.dumps(trend),
    }

    return render(
        request,
        'dashboard/owner_dashboard.html',
        context
    )


@login_required
def member_detail(request, user_id):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)
    member         = get_object_or_404(User, id=user_id)
    member_profile = get_object_or_404(UserProfile, user=member)
    context = {
        'member': member,
        'member_profile': member_profile,
        'attendance_records': Attendance.objects.filter(user=member)[:30],
        'payments': Payment.objects.filter(user=member),
        'workouts': WorkoutDay.objects.filter(user=member).prefetch_related('exercises'),
    }
    return render(request, 'owner/member_detail.html', context)


@login_required
@csrf_exempt
def update_payment(request, user_id):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)
    member = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        payment, _ = Payment.objects.get_or_create(user=member)
        payment.status = status
        payment.plan   = request.POST.get('plan', 'monthly')
        pd = request.POST.get('payment_date')
        ed = request.POST.get('expiry_date')
        if pd: payment.payment_date = pd
        if ed: payment.expiry_date  = ed
        payment.save()
        profile = member.profile
        profile.membership_status = 'active' if status == 'paid' else 'pending'
        profile.save()
        messages.success(request, f'Payment updated for {member.get_full_name()}')
        return redirect('owner_dashboard')
    payment = Payment.objects.filter(user=member).first()
    return render(request, 'owner/update_payment.html', {'member': member, 'payment': payment})


@login_required
def owner_attendance(request):
    get_object_or_404(UserProfile, user=request.user, is_owner=True)
    today       = date.today()
    filter_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
    context = {
        'attendances': Attendance.objects.filter(date=filter_date).select_related('user'),
        'filter_date': filter_date,
    }
    return render(request, 'owner/owner_attendance.html', context)


# ─── Profile ────────────────────────────────────────────────────────────────────

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
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def exercise_viewer(request):
    return render(request, "exercise_viewer.html")