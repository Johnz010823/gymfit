from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gym_app.models import UserProfile, WorkoutDay, Exercise, Payment, Attendance
from django.utils import timezone
from datetime import date, timedelta
import random


WORKOUT_PLANS = {
    'Monday': {
        'muscle_group': 'Chest & Triceps',
        'exercises': [
            ('Bench Press', 4, 10),
            ('Incline Dumbbell Press', 3, 12),
            ('Cable Flyes', 3, 15),
            ('Triceps Pushdown', 3, 12),
            ('Skull Crushers', 3, 10),
        ]
    },
    'Tuesday': {
        'muscle_group': 'Back & Biceps',
        'exercises': [
            ('Pull-ups', 4, 8),
            ('Barbell Row', 4, 10),
            ('Lat Pulldown', 3, 12),
            ('Bicep Curls', 3, 12),
            ('Hammer Curls', 3, 12),
        ]
    },
    'Wednesday': {
        'muscle_group': 'Rest Day',
        'exercises': [],
        'rest': True
    },
    'Thursday': {
        'muscle_group': 'Legs',
        'exercises': [
            ('Barbell Squat', 4, 10),
            ('Leg Press', 4, 12),
            ('Romanian Deadlift', 3, 10),
            ('Leg Curls', 3, 12),
            ('Calf Raises', 4, 15),
        ]
    },
    'Friday': {
        'muscle_group': 'Shoulders',
        'exercises': [
            ('Overhead Press', 4, 10),
            ('Lateral Raises', 4, 15),
            ('Front Raises', 3, 12),
            ('Face Pulls', 3, 15),
            ('Shrugs', 3, 15),
        ]
    },
    'Saturday': {
        'muscle_group': 'Full Body / Cardio',
        'exercises': [
            ('Deadlift', 3, 8),
            ('Push-ups', 3, 20),
            ('Treadmill Run', 1, 30),
            ('Plank', 3, 60),
        ]
    },
    'Sunday': {
        'muscle_group': 'Rest Day',
        'exercises': [],
        'rest': True
    },
}


class Command(BaseCommand):
    help = 'Creates demo data including gym owner, members, workouts, and attendance'

    def handle(self, *args, **kwargs):
        # Create superuser / gym owner
        if not User.objects.filter(username='owner').exists():
            owner = User.objects.create_superuser(
                username='owner',
                email='owner@gymfit.com',
                password='owner123',
                first_name='Juan',
                last_name='dela Cruz'
            )
            profile = owner.profile
            profile.is_owner = True
            profile.membership_status = 'active'
            profile.save()
            self.stdout.write(self.style.SUCCESS('✓ Gym Owner created: owner / owner123'))
        else:
            owner = User.objects.get(username='owner')
            self.stdout.write('Owner already exists')

        # Create demo members
        demo_members = [
            ('maria', 'maria@example.com', 'Maria', 'Santos', 'member123'),
            ('jose', 'jose@example.com', 'Jose', 'Reyes', 'member123'),
            ('ana', 'ana@example.com', 'Ana', 'Garcia', 'member123'),
        ]

        for username, email, first, last, password in demo_members:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first,
                    last_name=last
                )

                # Create workout plan
                for day, plan in WORKOUT_PLANS.items():
                    wd = WorkoutDay.objects.create(
                        user=user,
                        day=day,
                        muscle_group=plan['muscle_group'],
                        is_rest_day=plan.get('rest', False)
                    )
                    for ex_name, sets, reps in plan['exercises']:
                        Exercise.objects.create(
                            workout_day=wd,
                            name=ex_name,
                            sets=sets,
                            reps=reps
                        )

                # Create payment
                today = date.today()
                expiry = today + timedelta(days=30)
                Payment.objects.create(
                    user=user,
                    status='paid',
                    plan='monthly',
                    amount=500,
                    payment_date=today,
                    expiry_date=expiry,
                )
                profile = user.profile
                profile.membership_status = 'active'
                profile.save()

                # Create attendance records (last 14 days, random)
                for i in range(14, 0, -1):
                    d = today - timedelta(days=i)
                    if d.weekday() < 6 and random.random() > 0.3:
                        Attendance.objects.get_or_create(
                            user=user,
                            date=d,
                            defaults={
                                'time_in': timezone.now().replace(
                                    hour=random.randint(6, 10),
                                    minute=random.randint(0, 59)
                                ).time(),
                                'login_method': 'face'
                            }
                        )

                self.stdout.write(self.style.SUCCESS(f'✓ Member created: {username} / {password}'))
            else:
                self.stdout.write(f'{username} already exists')

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data setup complete!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Gym Owner:  owner / owner123')
        self.stdout.write('  Member 1:   maria / member123')
        self.stdout.write('  Member 2:   jose  / member123')
        self.stdout.write('  Member 3:   ana   / member123')

