# ASIET TALENT HUB

> **AI-Powered Campus Recruitment and Talent Discovery Platform for Adi Shankara Institute of Engineering and Technology (ASIET)**

ASIET TALENT HUB is a college-exclusive campus recruitment and talent discovery ecosystem connecting **ASIET engineering students** with **verified corporate recruiters** and the **Placement Cell**. The platform features AI-driven job matching, NLP candidate search, automated recruiter verification workflows, and single-dashboard administration via the native Django Admin panel.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
  - [Student Features](#student-features)
  - [Recruiter Features](#recruiter-features)
  - [Admin Features (Placement Cell Control Center)](#admin-features-placement-cell-control-center)
  - [AI & Recommendation Engine Features](#ai--recommendation-engine-features)
- [Recruiter Verification Workflow](#recruiter-verification-workflow)
- [Student Recruitment Workflow](#student-recruitment-workflow)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Project](#running-the-project)
- [Django Admin Control Center](#django-admin-control-center)
- [Testing](#testing)
- [Security & Authorization](#security--authorization)
- [Future Scope](#future-scope)

---

## Project Overview

**ASIET TALENT HUB** bridges the gap between campus talent at **Adi Shankara Institute of Engineering and Technology** and industry recruiters. Built on Django 5.0.2, it provides role-isolated experiences for students, approved company recruiters, and placement admins.

Key Highlights:
- **Prevent Scam & Fraudulent Job Postings**: All corporate recruiter accounts require verification by the ASIET Placement Cell before job postings or candidate resume access are unlocked.
- **Explainable AI Match Scores**: Every candidate application and job recommendation calculates an explainable match percentage (0–100%) based on required/preferred skills, department eligibility, CGPA, and NLP project/experience relevance using **spaCy**.
- **Unified Central Management**: All administrator controls (recruiter verification, job oversight, application tracking) are integrated directly into the standard Django Admin (`/admin/`).

---

## Key Features

### Student Features
- **Registration & Authentication**: Student sign-up with ASIET institutional email integration.
- **Rich Student Profile**: Manage personal info, academic details (Course, Department, CGPA, Graduation Year), technical skills, work experience, projects, and bio.
- **Profile Picture & Resume Management**: Upload PDF resumes and profile pictures with fallback initials avatar rendering (`ui-avatars.com`).
- **Campus Job & Internship Discovery**: Filter opportunities by opportunity type (*Full-Time*, *Internship*), work mode (*On-site*, *Remote*, *Hybrid*), eligible departments, and required skills.
- **Personalized Recommendations**: View job recommendations ordered by AI match score percentage.
- **One-Click Job Application**: Auto-fills profile info, default resume, and optional cover notes.
- **Duplicate Prevention**: Database uniqueness constraints prevent multi-submitting for the same position.
- **Application Tracking**: Monitor real-time status updates (*Applied*, *Under Review*, *Shortlisted*, *Interview Scheduled*, *Selected*, *Rejected*).
- **Save Jobs**: Bookmark job opportunities for later review.

### Recruiter Features
- **Company & Recruiter Registration**: Register company name, HR contact details, official email, phone, location, website, and industry.
- **Verification Status Lifecycle**: Account starts as `Pending Verification` until verified by Placement Cell Admin.
- **Recruiter Dashboard**: Access metrics for Active Jobs, Total Applications Received, Shortlisted Candidates, and Closed Roles.
- **Job & Internship Posting**: Publish postings specifying title, opportunity type, work mode, required/preferred skills, eligible branches, minimum CGPA, salary/stipend, and deadline.
- **Applicant Review & Candidate Evaluation**: Inspect candidate applications sorted by AI match score, view student profiles and uploaded PDF resumes, and update applicant statuses.
- **Verified Badge**: Approved company profiles and job postings display the **`✓ Verified by ASIET`** badge.

### Admin Features (Placement Cell Control Center)
- **Central Control via Django Admin (`/admin/`)**: Full administration through the standard Django Admin interface.
- **Recruiter Verification Management**: Filter recruiters by `Pending`, `Approved`, `Rejected`, and `Suspended`.
- **Bulk Admin Actions**: One-click actions to **Approve Selected Recruiters**, **Reject Selected Recruiters** (with rejection reasons), or **Suspend Selected Recruiters**.
- **Job & Application Oversight**: Close, activate, or deactivate job postings; view applicant counts and AI match scores.
- **Student Data Management**: Inspect and manage student records, profile completion %, academic details, and resumes.

### AI & Recommendation Engine Features
- **NLP Text Relevance Matching**: Uses **spaCy** (`en_core_web_sm`) to parse and match student project/experience text against job requirements.
- **Multi-Pillar Match Algorithm**:
  1. *Required & Preferred Technical Skills* (50 points)
  2. *Department Eligibility* (20 points)
  3. *Minimum CGPA Compliance* (15 points)
  4. *NLP Text Relevance* (15 points)
- **Explainable Checklist**: Generates user-friendly match explanations (e.g. `✓ Eligible Department (Computer Science)`, `✓ CGPA 8.8 meets minimum requirement (7.5)`).

---

## Recruiter Verification Workflow

```
Recruiter Registers Account (/recruiter/register/)
              │
              ▼
   Status = "Pending Verification"
 (Blocked from Job Creation & Talent Search)
              │
              ▼
  Placement Cell Reviews in Django Admin (/admin/)
              │
      ┌───────┴───────┐
      ▼               ▼
   Approve         Reject / Suspend
      │               │
      ▼               ▼
Approved Access   Access Denied
Verified Badge    (Blocked)
```

---

## Student Recruitment Workflow

```
Student Completes Profile & Resume
              │
              ▼
View AI Recommended Jobs & Campus Openings
              │
              ▼
Apply with Profile & Optional Cover Note
              │
              ▼
Recruiter Reviews Candidate & Match Score
              │
              ▼
Status Updated: Shortlisted / Interview / Selected
              │
              ▼
In-App Notification Sent to Student
```

---

## Technology Stack

- **Core Framework**: Python 3.10+, Django 5.0.2
- **Database**: SQLite (Development) / MySQL (Production support via `mysqlclient 2.2.4`)
- **Natural Language Processing**: spaCy 3.7.4 (`en_core_web_sm` model)
- **Frontend Architecture**: HTML5, Vanilla CSS3, JavaScript (ES6)
- **UI Styling & Icons**: Bootstrap 5.3, FontAwesome 6
- **Media Asset Processing**: Pillow 10.2.0 (Image upload & validation)
- **Environment Management**: python-dotenv 1.0.1

---

## Project Structure

```
ASIET_Discovery/
├── core/
│   ├── migrations/          # Database migrations
│   ├── admin.py             # Django Admin control center & recruiter verification
│   ├── context_processors.py# Global navbar context, roles & badges
│   ├── decorators.py        # Role-based access control decorators
│   ├── forms.py             # Student, recruiter, company & job forms
│   ├── models.py            # Student, CompanyProfile, Job, JobApplication, SavedJob, Notification models
│   ├── recommendations.py   # AI match score engine & spaCy NLP matching
│   ├── urls.py              # App routing
│   ├── views.py             # Views for student, recruiter, and public portals
│   └── tests.py             # Automated unit test suite (12 test scenarios)
├── ssv_discovery/
│   ├── settings.py          # Django project settings
│   ├── urls.py              # Root URL routing & media serving
│   └── wsgi.py              # WSGI application entry
├── templates/
│   ├── base.html            # Base template with role navigation
│   └── core/
│       ├── home.html        # Landing page with stats & active jobs
│       ├── discover.html    # Natural language talent search
│       ├── profile.html     # Student profile edit view
│       ├── recruiter/       # Recruiter registration, dashboard, applicants, job form
│       └── student/         # Student dashboard, jobs list, detail, applications
├── seed_data.py             # Database seed script for testing
├── requirements.txt         # Project dependencies
├── manage.py                # Django management script
└── README.md                # Project documentation
```

---

## Installation & Setup

### Prerequisites
- **Python 3.10+** installed
- **Git** installed

### Step-by-Step Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ABHILASHR0Y/-asiet-talent-hub.git
   cd ASIET_Discovery
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify spaCy Model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   DEBUG=True
   SECRET_KEY=your-django-secret-key-here
   ALLOWED_HOSTS=127.0.0.1,localhost
   ```

6. **Run Database Migrations**:
   ```bash
   python manage.py migrate
   ```

7. **Create Superuser (Placement Cell Admin)**:
   ```bash
   python manage.py createsuperuser
   ```

8. **Seed Sample Data (Optional)**:
   ```bash
   python seed_data.py
   ```

9. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

---

## Environment Variables

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DEBUG` | Enable/disable debug mode | `True` |
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | `127.0.0.1,localhost` |

---

## Database Setup

By default, the platform runs on **SQLite** for zero-configuration local development (`db.sqlite3`). For production deployment, configure MySQL in `ssv_discovery/settings.py` using `mysqlclient`.

---

## Running the Project

Start the Django development server:
```bash
python manage.py runserver
```

Access the endpoints:
- **Main Portal**: http://127.0.0.1:8000/
- **Placement Cell Admin**: http://127.0.0.1:8000/admin/

---

## Django Admin Control Center

Log in to http://127.0.0.1:8000/admin/ using superuser credentials:
- **Recruiter Verification**: View all company registrations, filter by pending status, and approve/reject/suspend recruiters with bulk actions.
- **Job Oversight**: Review active and expired postings, close or deactivate inappropriate jobs.
- **Application Analytics**: Monitor student application volume and AI candidate match percentages.

---

## Testing

Run the automated test suite:
```bash
python manage.py test core
```

**Current Test Results**:
```text
Ran 12 tests in 5.784s
OK (0 failures, 0 errors)
```

Verified Test Scenarios:
1. `test_01_recruiter_registration_pending_status` — Company registration sets status to `pending`
2. `test_02_pending_recruiter_blocked_from_posting_jobs` — Pending recruiters blocked from posting
3. `test_03_admin_approves_recruiter` — Admin recruiter approval workflow
4. `test_04_approved_recruiter_creates_job` — Approved recruiter publishes job
5. `test_05_job_appears_for_eligible_students` — Job visibility in student portal
6. `test_06_recommendation_and_match_score` — AI match score calculation
7. `test_07_and_08_student_apply_and_duplicate_prevention` — Job application & duplicate prevention
8. `test_09_10_11_recruiter_applicant_review_and_status_update` — Candidate review & status updates
9. `test_13_recruiter_authorization_isolation` — Cross-company isolation
10. `test_14_student_cannot_access_admin_or_recruiter_pages` — Role restriction enforcement
11. `test_15_expired_job_cannot_accept_applications` — Expiration logic enforcement
12. `test_16_suspended_recruiter_functions_blocked` — Suspended recruiter restriction enforcement

---

## Security & Authorization

- **Role Isolation**: Strict URL and view protection via `@approved_recruiter_required`, `@student_required`, and `@placement_admin_required`.
- **Company Data Isolation**: Recruiters can only access candidate applications submitted to their own company's jobs.
- **Backend Validation**: Access checks verify `verification_status == 'approved'` on the server side.
- **Data Protection**: Sensitive credentials and environment settings are kept out of version control via `.gitignore`.

---

## Future Scope

- **AI Resume Parsing**: Automatic skill extraction from uploaded PDF resumes.
- **Interview Scheduler**: Built-in calendar integration for scheduling online/offline interview rounds.
- **Email Notifications**: Automated email alerts via SMTP for status updates and verification approvals.
- **Placement Analytics & Prediction**: Machine learning prediction of student placement likelihood based on academic performance and skill profiles.

---

## License

This project is developed for **Adi Shankara Institute of Engineering and Technology (ASIET)** campus recruitment operations.
