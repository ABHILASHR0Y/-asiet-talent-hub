# ASIET TALENT HUB

A college-exclusive, AI-powered campus recruitment platform for **Adi Shankara Institute of Engineering and Technology (ASIET)**. ASIET Talent Hub helps recruiters discover, evaluate, and hire ASIET students through natural language search, job postings, and intelligent recommendations.

## Features

- **Natural Language Search**: Find talent using conversational queries
- **Advanced Filtering**: Refine results by skills, experience level, and location
- **Student Profile Management**: Complete profile creation with skills, experience, and projects
- **Modern UI/UX**: Clean, responsive design optimized for all devices
- **Admin Dashboard**: Platform analytics and user management
- **Secure Authentication**: User-friendly registration and login process

## Technology Stack

- **Backend**: Django 5.0.2
- **Database**: SQLite (development) / MySQL (production-ready)
- **Frontend**: HTML5, CSS3, JavaScript
- **NLP**: spaCy for natural language processing
- **Styling**: Bootstrap 5 with custom CSS

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ASIET_Discovery
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the spaCy model (included via requirements.txt):
```bash
python -m spacy download en_core_web_sm
```

5. Configure environment variables:
   - Create a `.env` file in the project root with the following content:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   STATIC_URL=/static/
   STATIC_ROOT=staticfiles
   ```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Collect static files:
```bash
python manage.py collectstatic
```

9. Run the development server:
```bash
python manage.py runserver
```

### Accessing the Application

- **Main Application**: Visit http://127.0.0.1:8000/
- **Admin Interface**: Visit http://127.0.0.1:8000/admin

## Usage Guide

### For Recruiters

1. Visit the Discover page to search for talent
2. Use natural language queries like "Python developers with ML experience"
3. Apply filters to refine your search results
4. View student profiles and contact them directly

### For Students

1. Register for an account
2. Complete your profile with skills, experience, and projects
3. Upload your resume and profile picture
4. Your profile will be discoverable by recruiters

## About ASIET

**ASIET TALENT HUB** is the official campus recruitment platform for **Adi Shankara Institute of Engineering and Technology (ASIET)**, connecting ASIET students with recruiters and placement opportunities.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
