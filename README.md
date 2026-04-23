# GymFit Pro — AI-Powered Gym Attendance & Workout Management

A full-featured Django web application with facial recognition check-in,
Google OAuth login, workout tracking, and a comprehensive owner dashboard.

---

## 📁 Project Structure

```
gym_site/
├── gym_site/               ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── gym_app/                ← Main application
│   ├── models.py           ← DB models (UserProfile, Payment, Workout, Attendance)
│   ├── views.py            ← All views
│   ├── urls.py             ← URL routing
│   ├── admin.py            ← Admin panel registration
│   ├── signals.py          ← Auto-create user profiles
│   ├── apps.py
│   ├── templatetags/
│   │   └── gym_tags.py     ← Custom template filter
│   └── management/
│       └── commands/
│           └── setup_demo.py  ← Demo data seeder
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── account/login.html  ← Custom allauth login
│   ├── dashboard/
│   │   ├── member_dashboard.html
│   │   ├── owner_dashboard.html
│   │   ├── attendance.html
│   │   └── profile.html
│   ├── face/
│   │   ├── face_register.html
│   │   └── face_login.html
│   ├── workouts/
│   │   └── workout_plan.html
│   └── owner/
│       ├── member_detail.html
│       ├── update_payment.html
│       └── owner_attendance.html
├── static/
│   ├── css/main.css
│   └── js/main.js
├── face_data/              ← Auto-created; stores face encodings (.pkl files)
├── media/                  ← User uploads
├── manage.py
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- pip
- (Optional but recommended) virtualenv or venv
- PyCharm IDE

### 2. Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

**Basic install (without face recognition):**
```bash
pip install Django==4.2.7 django-allauth==0.57.0 Pillow==10.1.0 requests python-decouple
```

**Full install (with face recognition):**
> ⚠️ `dlib` requires CMake and a C++ compiler.
> On Windows: install Visual Studio Build Tools first.
> On Ubuntu: `sudo apt-get install cmake build-essential libopenblas-dev liblapack-dev`

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
cd gym_site
python manage.py makemigrations
python manage.py migrate
```

### 5. Set up sites framework

```bash
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'GymFit Pro'})
"
```

### 6. Load demo data

```bash
python manage.py setup_demo
```

This creates:
| Role       | Username | Password    |
|------------|----------|-------------|
| Gym Owner  | owner    | owner123    |
| Member     | maria    | member123   |
| Member     | jose     | member123   |
| Member     | ana      | member123   |

### 7. Run the development server

```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

---

## 🔑 Google OAuth Setup (Optional)

To enable "Sign in with Google":

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → APIs & Services → Credentials
3. Create **OAuth 2.0 Client ID** (Web Application)
4. Add authorized redirect URI: `http://localhost:8000/accounts/google/callback/`
5. Copy **Client ID** and **Client Secret**
6. Open `gym_site/settings.py` and update:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'YOUR_ACTUAL_CLIENT_ID',
            'secret':    'YOUR_ACTUAL_CLIENT_SECRET',
            'key':       ''
        },
        ...
    }
}
```

7. Or configure it via Django Admin:
   - Go to `/admin/`
   - Social Applications → Add → Google
   - Paste your client ID and secret
   - Assign to site `localhost:8000`

---

## 🎭 Face Recognition

Face recognition uses the `face_recognition` Python library (built on dlib).

**How it works:**
1. User logs in via Google or credentials
2. Opens `/face/register/` → webcam captures face → encoding saved as `.pkl` file
3. At `/face/login/` → webcam scans face → compared against all stored encodings
4. Match found → user logged in + attendance marked automatically

**Demo mode:** If `face_recognition` is not installed, the system falls back to demo mode — face registration still works (stored as placeholder), but matching is skipped.

---

## 🏋️ Features Summary

### Member Features
- ✅ Google OAuth login
- ✅ Face registration & login
- ✅ Auto attendance marking on face login
- ✅ Daily workout plan with per-exercise completion toggle
- ✅ Workout logs & history
- ✅ 7-day attendance chart (Chart.js)
- ✅ Membership/payment status display
- ✅ Profile management

### Owner Dashboard
- ✅ Overview stats (total members, present today, paid, expired)
- ✅ 7-day attendance trend chart
- ✅ Full member list with status
- ✅ Per-member detail view (attendance, payments, workouts)
- ✅ Payment management (status, plan, dates)
- ✅ Attendance filter by date

---

## 🛠️ Tech Stack

| Layer       | Technology                      |
|-------------|----------------------------------|
| Backend     | Django 4.2                      |
| Auth        | Django Allauth + Google OAuth   |
| Face AI     | face_recognition + OpenCV + dlib|
| Database    | SQLite (default)                |
| Frontend    | Bootstrap 5, Chart.js, vanilla JS|
| Fonts       | Bebas Neue + Inter (Google Fonts)|
| Icons       | Font Awesome 6                  |

---

## 🚀 PyCharm Setup

1. Open PyCharm → **File → Open** → select the `gym_site/` folder
2. Configure Python interpreter: **Settings → Python Interpreter** → select your venv
3. Run config: Edit Configurations → Add → Django → set script to `manage.py`, params to `runserver`
4. Click **Run** ▶

---

## 📦 Upgrading to PostgreSQL (Optional)

```bash
pip install psycopg2-binary
```

In `settings.py`, replace DATABASES with:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gymfit_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 🔒 Security Notes

- Face encodings are stored as encrypted pickle files in `face_data/` (server-side only)
- In production, set `DEBUG = False` and configure a real `SECRET_KEY`
- Use HTTPS in production (required for webcam access on non-localhost)
- Restrict `ALLOWED_HOSTS` to your domain

---

*Built with Django · Powered by face_recognition · Styled dark and bold*
