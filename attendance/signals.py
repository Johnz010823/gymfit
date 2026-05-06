from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from datetime import date

from gym_app.models import Attendance


@receiver(user_logged_in)
def auto_mark_attendance(sender, request, user, **kwargs):
    """
    Fires on every successful login — credential or face.
    Determines the method from the session flag set by the face-login view,
    otherwise defaults to 'credentials'.
    """
    today    = date.today()
    already  = Attendance.objects.filter(user=user, date=today).exists()

    if not already:
        # Face-login view should set request.session['login_method'] = 'face'
        # before calling Django's login(). Credential login won't set it.
        method    = request.session.pop('login_method', 'credentials')
        local_now = timezone.localtime(timezone.now())

        Attendance.objects.create(
            user=user,
            date=today,
            time_in=local_now.time(),
            login_method=method,
        )