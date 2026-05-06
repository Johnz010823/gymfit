import random
import json
import os
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ExerciseLibrary, WorkoutDay
from gym_app.models import User, WorkoutDay, Exercise, WorkoutLog

# ─── Exercise Library ──────────────────────────────────────────────────────────

EXERCISE_LIBRARY = {
    'Chest': {
        'icon': '🏋️', 'color': 'danger',
        'subcategories': {
            'Compound':  ['Bench Press (Barbell)', 'Bench Press (Dumbbell)', 'Incline Bench Press',
                          'Decline Bench Press', 'Chest Press Machine', 'Dips', 'Push-ups', 'Incline Dumbbell Press'],
            'Isolation': ['Cable Flyes', 'Pec Deck Machine', 'Dumbbell Flyes', 'Cable Crossover'],
        },
    },
    'Back': {
        'icon': '🦾', 'color': 'primary',
        'subcategories': {
            'Vertical Pull':       ['Pull-ups', 'Chin-ups', 'Lat Pulldown (Wide Grip)', 'Lat Pulldown (Narrow Grip)'],
            'Rows':                ['Barbell Row', 'One-Arm Dumbbell Row', 'Seated Cable Row', 'T-Bar Row', 'Chest-Supported Row'],
            'Lower Back & Traps':  ['Deadlift', 'Rack Pulls', 'Barbell Shrugs', 'Hyperextensions'],
        },
    },
    'Shoulders': {
        'icon': '💪', 'color': 'warning',
        'subcategories': {
            'Pressing':            ['Overhead Press (Military Press)', 'Arnold Press', 'Seated Dumbbell Press', 'Push Press'],
            'Raises & Isolation':  ['Lateral Raise', 'Front Raise', 'Face Pulls', 'Reverse Pec Deck', 'Rear Delt Fly'],
        },
    },
    'Legs': {
        'icon': '🦵', 'color': 'success',
        'subcategories': {
            'Quads':               ['Barbell Squat (Back)', 'Barbell Squat (Front)', 'Leg Press', 'Hack Squat',
                                    'Leg Extensions', 'Bulgarian Split Squats', 'Lunges'],
            'Hamstrings & Glutes': ['Romanian Deadlift (RDL)', 'Stiff-Leg Deadlift', 'Leg Curls (Lying)',
                                    'Leg Curls (Seated)', 'Hip Thrusts', 'Glute Bridges', 'Kettlebell Swings'],
            'Calves':              ['Standing Calf Raise', 'Seated Calf Raise', 'Donkey Calf Raise'],
        },
    },
    'Arms': {
        'icon': '💪', 'color': 'info',
        'subcategories': {
            'Biceps':   ['Barbell Curl', 'Dumbbell Curl', 'Hammer Curl', 'Preacher Curl', 'Concentration Curl', '21s'],
            'Triceps':  ['Triceps Pushdown (Rope)', 'Triceps Pushdown (Bar)', 'Skull Crushers',
                         'Close-Grip Bench Press', 'Overhead Triceps Extension', 'Tricep Dips', 'Kickbacks'],
        },
    },
    'Core': {
        'icon': '🔥', 'color': 'secondary',
        'subcategories': {
            'Stability':           ['Plank', 'Side Plank', 'Bird-Dog', 'Dead Bug'],
            'Flexion & Rotation':  ['Hanging Leg Raise', 'Russian Twists', 'Cable Woodchoppers',
                                    'Ab Wheel Rollouts', 'Crunches'],
        },
    },
    'Full Body & Cardio': {
        'icon': '🏃', 'color': 'dark',
        'subcategories': {
            'Full Body': ['Clean and Jerk', 'Snatch', 'Burpees', 'Thrusters'],
            'Cardio':    ['Treadmill Run', 'Elliptical', 'Stairmaster', 'Stationary Bike',
                          'Rowing Machine', 'Battle Ropes'],
        },
    },
}

DAY_PLAN = {
    'Monday':    {'muscle_group': 'Chest & Triceps',   'picks': [('Chest', 3),    ('Arms', 2, 'Triceps')]},
    'Tuesday':   {'muscle_group': 'Back & Biceps',     'picks': [('Back', 3),     ('Arms', 2, 'Biceps')]},
    'Wednesday': {'muscle_group': 'Legs',              'picks': [('Legs', 4)]},
    'Thursday':  {'muscle_group': 'Shoulders & Core',  'picks': [('Shoulders', 3), ('Core', 2)]},
    'Friday':    {'muscle_group': 'Arms',              'picks': [('Arms', 3, 'Biceps'), ('Arms', 3, 'Triceps')]},
    'Saturday':  {'muscle_group': 'Full Body & Cardio','picks': [('Full Body & Cardio', 4)]},
    'Sunday':    None,
}

DEFAULT_SETS_REPS = {
    'Chest': (4, 10), 'Back': (4, 10), 'Shoulders': (3, 12),
    'Legs':  (4, 10), 'Arms': (3, 12), 'Core':      (3, 30),
    'Full Body & Cardio': (3, 10),
}


def _random_exercises_for_day(day):
    """
    Returns (muscle_group, [(name, sets, reps), ...]) picked randomly.
    No seed — each call returns different exercises so every user gets unique suggestions.
    """
    plan = DAY_PLAN.get(day)
    if plan is None:
        return None, None

    muscle_group = plan['muscle_group']
    exercises = []

    for pick in plan['picks']:
        category      = pick[0]
        count         = pick[1]
        subcat_filter = pick[2] if len(pick) > 2 else None
        cat_data      = EXERCISE_LIBRARY.get(category, {})
        subcats       = cat_data.get('subcategories', {})

        pool = []
        for subcat_name, ex_list in subcats.items():
            if subcat_filter and subcat_filter.lower() not in subcat_name.lower():
                continue
            pool.extend(ex_list)

        rng    = random.Random(os.urandom(16))  # fresh seed every call → unique per user
        chosen = rng.sample(pool, min(count, len(pool)))
        sets, reps = DEFAULT_SETS_REPS.get(category, (3, 10))
        for name in chosen:
            exercises.append((name, sets, reps))

    return muscle_group, exercises


# ─── Views ────────────────────────────────────────────────────────────────────

@login_required
def workout_plan(request):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    workout_days = [
        (day, WorkoutDay.objects.filter(user=request.user, day=day).prefetch_related('exercises').first())
        for day in days
    ]
    context = {
        'workout_days':     workout_days,
        'profile':          request.user.profile,
        'today_name':       date.today().strftime('%A'),
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
                user=request.user,
                exercise=exercise,
                exercise_name=exercise.name,
                sets_completed=exercise.sets,
                reps_completed=exercise.reps,
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
    wd, created = WorkoutDay.objects.get_or_create(
        user=request.user, day=day,
        defaults={'muscle_group': '', 'is_rest_day': True}
    )
    if not created:
        wd.is_rest_day = not wd.is_rest_day
        wd.save()
    label = 'rest' if wd.is_rest_day else 'training'
    messages.success(request, f'{day} is now a {label} day.')
    return redirect('workout_plan')


@login_required
def suggest_workout(request):
    today_name = date.today().strftime('%A')
    muscle_group, exercises = _random_exercises_for_day(today_name)

    if exercises is None:
        messages.info(request, '😴 Today is Sunday — rest and recover!')
        return redirect('workout_plan')

    wd, _ = WorkoutDay.objects.get_or_create(
        user=request.user, day=today_name,
        defaults={'muscle_group': muscle_group, 'is_rest_day': False}
    )
    wd.muscle_group = muscle_group
    wd.is_rest_day  = False
    wd.save()

    # Clear existing exercises and replace with fresh suggestion
    wd.exercises.all().delete()
    for name, sets, reps in exercises:
        Exercise.objects.create(workout_day=wd, name=name, sets=sets, reps=reps)

    messages.success(request, f'⚡ Fresh {muscle_group} workout ready for {today_name}!')
    return redirect('workout_plan')


@login_required
def exercise_library_view(request, day):
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if day not in valid_days:
        messages.error(request, 'Invalid day.')
        return redirect('workout_plan')

    wd, _ = WorkoutDay.objects.get_or_create(
        user=request.user, day=day,
        defaults={'muscle_group': day, 'is_rest_day': False}
    )
    if wd.is_rest_day:
        wd.is_rest_day = False
        wd.save()

    existing = list(wd.exercises.values_list('name', flat=True))
    context = {
        'day':                day,
        'workout_day':        wd,
        'exercise_library':   EXERCISE_LIBRARY,
        'existing_exercises': existing,
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

    wd, _ = WorkoutDay.objects.get_or_create(
        user=request.user, day=day,
        defaults={'muscle_group': muscle_group or day, 'is_rest_day': False}
    )
    if muscle_group:
        wd.muscle_group = muscle_group
    wd.is_rest_day = False
    wd.save()

    added, skipped = [], []
    for ex in exercises_data:
        name = ex.get('name', '').strip()
        if not name:
            continue
        sets      = int(ex.get('sets', 3))
        reps      = int(ex.get('reps', 10))
        weight    = ex.get('weight') or None
        weight_kg = float(weight) if weight else None
        _, created = Exercise.objects.get_or_create(
            workout_day=wd, name=name,
            defaults={'sets': sets, 'reps': reps, 'weight_kg': weight_kg}
        )
        (added if created else skipped).append(name)

    parts = []
    if added:   parts.append(f'{len(added)} exercise(s) added')
    if skipped: parts.append(f'{len(skipped)} already in plan')
    return JsonResponse({
        'success': True,
        'message': ', '.join(parts) + f' for {day}.',
        'added':   added,
        'skipped': skipped,
    })


@login_required
def add_exercise(request, day):
    """Manual text-entry fallback."""
    wd, _ = WorkoutDay.objects.get_or_create(
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
            return render(request, 'workouts/add_exercise.html',
                          {'day': day, 'exercise_library': EXERCISE_LIBRARY})
        Exercise.objects.create(
            workout_day=wd, name=name,
            sets=int(sets), reps=int(reps),
            weight_kg=float(weight) if weight else None,
        )
        messages.success(request, f'"{name}" added to {day}!')
        return redirect('workout_plan')
    return render(request, 'workouts/add_exercise.html',
                  {'day': day, 'exercise_library': EXERCISE_LIBRARY})


@login_required
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, workout_day__user=request.user)
    if request.method == 'POST':
        name   = request.POST.get('name', '').strip()
        sets   = request.POST.get('sets', exercise.sets)
        reps   = request.POST.get('reps', exercise.reps)
        weight = request.POST.get('weight', '')
        if not name:
            messages.error(request, 'Please select an exercise.')
            return render(request, 'workouts/edit_exercise.html',
                          {'exercise': exercise, 'exercise_library': EXERCISE_LIBRARY})
        exercise.name      = name
        exercise.sets      = int(sets)
        exercise.reps      = int(reps)
        exercise.weight_kg = float(weight) if weight else None
        exercise.save()
        messages.success(request, f'"{name}" updated!')
        return redirect('workout_plan')
    return render(request, 'workouts/edit_exercise.html',
                  {'exercise': exercise, 'exercise_library': EXERCISE_LIBRARY})


@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, workout_day__user=request.user)
    if request.method == 'POST':
        name = exercise.name
        exercise.delete()
        messages.success(request, f'"{name}" removed.')
    return redirect('workout_plan')


@login_required
def add_exercise_from_library(request, day, ex_id):
    exercise   = get_object_or_404(ExerciseLibrary, id=ex_id)
    workout_day, _ = WorkoutDay.objects.get_or_create(user=request.user, day=day)
    Exercise.objects.get_or_create(
        workout_day=workout_day,
        name=exercise.name,
        defaults={'sets': 3, 'reps': 10}
    )
    return redirect('workout_plan')
