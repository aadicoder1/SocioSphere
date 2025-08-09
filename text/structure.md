# 🌐 SocioSphere - Project Development Plan

A web application to bridge citizens with NGOs and welfare organizations by enabling easy complaint submissions, animal rescue alerts, and environmental welfare reporting.

---

## 🚀 Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap (optional)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login, Werkzeug
- **Image Handling**: Flask Upload / base64
- **Location Tagging**: Manual entry (Phase 1), GPS/Maps API (Optional future)

---

## ✅ Phase 1: Project Setup & Base App

1. Initialize folder structure for Flask
2. Create `run.py` to start the app
3. Configure Flask in `app/__init__.py`
4. Basic route: `/` → homepage
5. Basic layout with `index.html` in templates

---

## 🔐 Phase 2: Authentication System

1. Setup SQLAlchemy DB
2. Create `User` model:
   - Fields: `username`, `email`, `password_hash`, `role`
3. Signup route and form
4. Login route and form
5. Logout route
6. Role-based access control:
   - Users: submit complaints
   - NGOs: view complaints dashboard

---

## 📝 Phase 3: Complaint System

1. Create `Complaint` model:
   - Fields: `title`, `description`, `image`, `location`, `status`, `user_id`
2. Form for complaint submission (users only)
3. Allow optional image uploads
4. Store complaints in database
5. Add timestamp and complaint status

---

## 📊 Phase 4: NGO Dashboard

1. NGO login → redirect to `/dashboard`
2. View all complaints submitted by users
3. Filter by status, date, etc.
4. Option to:
   - Mark as resolved
   - Add remarks (optional)
   - Delete (optional)

---

## 🎨 Phase 5: UI/UX Enhancements (Optional)

1. Use Bootstrap for better styling
2. Different dashboards for NGO and users
3. Show "My Complaints" for logged-in users
4. Flash messages and error handling
5. Responsive design for mobile & desktop

---

## 🧠 Phase 6: Advanced Features (Future Scope)

1. Google Maps / Location API for auto-location
2. Email notification system
3. NGO onboarding and approval system
4. Admin panel for platform-wide control
5. User complaint tracking with ticket ID

---

## 👥 User Roles Overview

### 1. Normal Users:
- Sign up / login
- Submit complaints with image & location
- View own complaints (future scope)

### 2. NGO:
- Login as NGO
- Access dashboard of complaints
- Manage status and responses

---

## 📁 Folder Structure (Flask)

SocioSphere/
│
├── run.py
├── requirements.txt
│
├── app/
│ ├── init.py
│ ├── models.py
│ ├── routes.py
│ ├── forms.py
│ ├── static/
│ │ └── (CSS, images)
│ └── templates/
│ ├── index.html
│ ├── login.html
│ ├── signup.html
│ ├── submit_complaint.html
│ ├── dashboard.html
│ └── layout.html
│
├── instance/
│ └── sociosphere.db














from app.extensions import db
from app.models import User

# Find the user by username or email
user = User.query.filter_by(username='aadicoder1').first()

# Check if user found
if user:
    user.role = 'admin'  # assign admin role
    db.session.commit()  # save changes
    print("User role updated successfully.")
else:
    print("User not found.")
