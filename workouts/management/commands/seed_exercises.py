from django.core.management.base import BaseCommand
from workouts.models import ExerciseLibrary

class Command(BaseCommand):
    help = 'Seed exercise library'

    def handle(self, *args, **kwargs):
        exercises = [

            # Chest
            ("Barbell Bench Press (Flat)", "Chest"),
            ("Dumbbell Bench Press", "Chest"),
            ("Incline Barbell Press", "Chest"),
            ("Incline Dumbbell Press", "Chest"),
            ("Decline Barbell Press", "Chest"),
            ("Chest Dips", "Chest"),
            ("Cable Flyes (High-to-Low)", "Chest"),
            ("Cable Flyes (Low-to-High)", "Chest"),
            ("Pec Deck Machine", "Chest"),
            ("Standard Push-ups", "Chest"),
            ("Diamond Push-ups", "Chest"),

            # Shoulder
            ("Military Press", "Shoulder"),
            ("Seated Dumbbell Press", "Shoulder"),
            ("Arnold Press", "Shoulder"),
            ("Lateral Raises", "Shoulder"),
            ("Cable Lateral Raises", "Shoulder"),
            ("Front Raises (Dumbbell)", "Shoulder"),
            ("Front Raises (Plate)", "Shoulder"),
            ("Face Pulls", "Shoulder"),
            ("Reverse Pec Deck", "Shoulder"),
            ("Upright Rows", "Shoulder"),
            ("Dumbbell Shrugs", "Shoulder"),
            ("Barbell Shrugs", "Shoulder"),

            # Back
            ("Deadlift", "Back"),
            ("Sumo Deadlift", "Back"),
            ("Pull-ups", "Back"),
            ("Chin-ups", "Back"),
            ("Lat Pulldown", "Back"),
            ("Close Grip Pulldown", "Back"),
            ("Barbell Row", "Back"),
            ("Bent-over Row", "Back"),
            ("Dumbbell Row", "Back"),
            ("Cable Row", "Back"),
            ("T-Bar Row", "Back"),
            ("Hyperextensions", "Back"),

            # Biceps
            ("Barbell Curls", "Biceps"),
            ("Dumbbell Curls", "Biceps"),
            ("Hammer Curls", "Biceps"),
            ("Preacher Curls", "Biceps"),
            ("Concentration Curls", "Biceps"),
            ("Incline Curls", "Biceps"),
            ("Spider Curls", "Biceps"),
            ("Cable Curls", "Biceps"),
            ("Reverse Curls", "Biceps"),
            ("Wrist Curls", "Biceps"),

            # Triceps
            ("Triceps Pushdown Rope", "Triceps"),
            ("Triceps Pushdown Bar", "Triceps"),
            ("Overhead Extension Dumbbell", "Triceps"),
            ("Overhead Extension Cable", "Triceps"),
            ("Skull Crushers", "Triceps"),
            ("Close Grip Bench", "Triceps"),
            ("Kickbacks", "Triceps"),
            ("Bench Dips", "Triceps"),

            # Legs
            ("Back Squat", "Legs"),
            ("Goblet Squat", "Legs"),
            ("Bulgarian Split Squat", "Legs"),
            ("Leg Press", "Legs"),
            ("Leg Extensions", "Legs"),
            ("Leg Curls", "Legs"),
            ("Romanian Deadlift", "Legs"),
            ("Walking Lunges", "Legs"),
            ("Seated Calf Raises", "Legs"),
            ("Standing Calf Raises", "Legs"),

            # Core
            ("Plank", "Core"),
            ("Side Plank", "Core"),
            ("Hanging Leg Raises", "Core"),
            ("Ab Wheel", "Core"),
            ("Russian Twists", "Core"),
            ("Cable Crunches", "Core"),
            ("Treadmill Sprint", "Core"),
            ("Incline Walk", "Core"),
        ]

        for name, category in exercises:
            ExerciseLibrary.objects.get_or_create(name=name, category=category)

        self.stdout.write(self.style.SUCCESS("Exercises seeded!"))