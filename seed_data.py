import os
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssv_discovery.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Student, CompanyProfile, Job, JobApplication, SavedJob, Notification, SkillFilter

def run_seed():
    print("Seeding sample recruitment data for ASIET Talent Hub...")

    # 1. Ensure Placement Cell Admin
    admin, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'placement@asiet.edu.in',
        'first_name': 'ASIET',
        'last_name': 'Placement Cell',
        'is_staff': True,
        'is_superuser': True
    })
    if created:
        admin.set_password('admin123')
        admin.save()
        print("-> Created Placement Admin (username: admin, pass: admin123)")

    # 2. Approved Recruiter 1: Infosys
    infy_user, created = User.objects.get_or_create(username='infosys_hr', defaults={
        'email': 'careers@infosys.com',
        'first_name': 'Vikram',
        'last_name': 'Mehta'
    })
    if created:
        infy_user.set_password('recruiter123')
        infy_user.save()

    infy_company, _ = CompanyProfile.objects.get_or_create(user=infy_user, defaults={
        'company_name': 'Infosys Limited',
        'hr_name': 'Vikram Mehta',
        'official_email': 'careers@infosys.com',
        'phone_number': '+91 9876543210',
        'website': 'https://www.infosys.com',
        'location': 'Bengaluru, India',
        'industry': 'IT Services & Consulting',
        'description': 'Infosys is a global leader in next-generation digital services and consulting.',
        'verification_status': 'approved',
        'verified_by': admin,
        'verified_at': timezone.now()
    })

    # Approved Recruiter 2: TCS
    tcs_user, created = User.objects.get_or_create(username='tcs_hr', defaults={
        'email': 'recruitment@tcs.com',
        'first_name': 'Priya',
        'last_name': 'Raman'
    })
    if created:
        tcs_user.set_password('recruiter123')
        tcs_user.save()

    tcs_company, _ = CompanyProfile.objects.get_or_create(user=tcs_user, defaults={
        'company_name': 'Tata Consultancy Services (TCS)',
        'hr_name': 'Priya Raman',
        'official_email': 'recruitment@tcs.com',
        'phone_number': '+91 9845012345',
        'website': 'https://www.tcs.com',
        'location': 'Kochi / Chennai',
        'industry': 'IT Services',
        'description': 'TCS is an IT services, consulting and business solutions organization.',
        'verification_status': 'approved',
        'verified_by': admin,
        'verified_at': timezone.now()
    })

    # Pending Recruiter 3: Innovate AI Labs
    inn_user, created = User.objects.get_or_create(username='innovate_hr', defaults={
        'email': 'careers@innovateai.io',
        'first_name': 'Alex',
        'last_name': 'Rivera'
    })
    if created:
        inn_user.set_password('recruiter123')
        inn_user.save()

    CompanyProfile.objects.get_or_create(user=inn_user, defaults={
        'company_name': 'Innovate AI Labs',
        'hr_name': 'Alex Rivera',
        'official_email': 'careers@innovateai.io',
        'phone_number': '+91 9123456789',
        'website': 'https://innovateai.io',
        'location': 'Kochi, Kerala',
        'industry': 'Artificial Intelligence',
        'description': 'Cutting edge startup developing generative AI models for enterprise analytics.',
        'verification_status': 'pending'
    })

    # 3. Create Sample Jobs
    now = timezone.now()
    job1, _ = Job.objects.get_or_create(
        title='Systems Engineer Trainee',
        company=infy_company,
        defaults={
            'posted_by': infy_user,
            'opportunity_type': 'full_time',
            'work_mode': 'on_site',
            'location': 'Bengaluru / Mysuru Campus',
            'description': 'Looking for talented engineering graduates to join Infosys Systems Engineering division. Strong foundation in programming and problem solving required.',
            'required_skills': 'Python, Java, SQL, Data Structures',
            'preferred_skills': 'Django, Cloud, Git',
            'eligible_departments': 'Computer Science, Electronics, Mechanical',
            'minimum_cgpa': Decimal('7.00'),
            'graduation_year': 2026,
            'salary_or_stipend': '₹5.50 LPA + Performance Bonus',
            'openings': 15,
            'deadline': now + timedelta(days=20),
            'selection_process': 'Online Aptitude Test -> Coding Assessment -> Technical & HR Interview',
            'status': 'active'
        }
    )

    job2, _ = Job.objects.get_or_create(
        title='AI/ML Research Intern',
        company=infy_company,
        defaults={
            'posted_by': infy_user,
            'opportunity_type': 'internship',
            'work_mode': 'hybrid',
            'location': 'Kochi / Remote',
            'description': 'Internship position focusing on Natural Language Processing, computer vision, and predictive analytics models using Python and PyTorch.',
            'required_skills': 'Python, Machine Learning, TensorFlow, PyTorch',
            'preferred_skills': 'spaCy, OpenCV, Docker',
            'eligible_departments': 'Computer Science, Information Technology',
            'minimum_cgpa': Decimal('8.00'),
            'graduation_year': 2026,
            'salary_or_stipend': '₹30,000 / month',
            'openings': 4,
            'deadline': now + timedelta(days=15),
            'selection_process': 'Project Evaluation -> Technical Interview',
            'status': 'active'
        }
    )

    job3, _ = Job.objects.get_or_create(
        title='Full Stack Developer (Digital Role)',
        company=tcs_company,
        defaults={
            'posted_by': tcs_user,
            'opportunity_type': 'full_time',
            'work_mode': 'on_site',
            'location': 'Kochi / Chennai',
            'description': 'TCS Digital hiring for web application development using modern frontend and backend technologies.',
            'required_skills': 'React, JavaScript, Python, Django, MySQL',
            'preferred_skills': 'Node.js, Docker, AWS',
            'eligible_departments': 'Computer Science, Electronics',
            'minimum_cgpa': Decimal('7.50'),
            'graduation_year': 2026,
            'salary_or_stipend': '₹7.00 LPA',
            'openings': 8,
            'deadline': now + timedelta(days=25),
            'selection_process': 'TCS NQT Assessment -> Technical Interview -> HR Round',
            'status': 'active'
        }
    )

    # 4. Create Students & Profiles
    s1_user, created = User.objects.get_or_create(username='rahul', defaults={
        'email': 'rahul.s@asiet.edu.in',
        'first_name': 'Rahul',
        'last_name': 'Sharma'
    })
    if created:
        s1_user.set_password('student123')
        s1_user.save()

    student1, _ = Student.objects.get_or_create(user=s1_user, defaults={
        'course': 'B.Tech',
        'department': 'Computer Science',
        'cgpa': Decimal('8.80'),
        'graduation_year': 2026,
        'phone_number': '+91 9811223344',
        'bio': 'Passionate web developer with expertise in Python, Django, React, and MySQL.',
        'skills': 'Python, Django, React, JavaScript, SQL, MySQL, Git',
        'experience': 'Software Development Intern at WebTech Kochi (3 months). Built REST APIs using Django.',
        'projects': 'ASIET Talent Hub platform, E-commerce web application with payment integration.'
    })

    s2_user, created = User.objects.get_or_create(username='ananya', defaults={
        'email': 'ananya.n@asiet.edu.in',
        'first_name': 'Ananya',
        'last_name': 'Nair'
    })
    if created:
        s2_user.set_password('student123')
        s2_user.save()

    student2, _ = Student.objects.get_or_create(user=s2_user, defaults={
        'course': 'B.Tech',
        'department': 'Computer Science',
        'cgpa': Decimal('9.20'),
        'graduation_year': 2026,
        'phone_number': '+91 9855667788',
        'bio': 'AI enthusiast and competitive programmer interested in Machine Learning and Deep Learning.',
        'skills': 'Python, Machine Learning, TensorFlow, PyTorch, spaCy, OpenCV, C++',
        'experience': 'Research Intern at Machine Learning Lab. Published paper on NLP text classification.',
        'projects': 'Automated document summarization engine, Object detection pipeline using OpenCV.'
    })

    # 5. Create Sample Applications
    app1, _ = JobApplication.objects.get_or_create(
        student=student1,
        job=job3,
        defaults={'status': 'shortlisted', 'cover_note': 'Extremely interested in TCS Digital role.'}
    )

    app2, _ = JobApplication.objects.get_or_create(
        student=student2,
        job=job2,
        defaults={'status': 'applied', 'cover_note': 'My background matches your AI research requirements.'}
    )

    # 6. Add default Skill Filters
    skills_list = [
        ('Python', 'Python'),
        ('Django', 'Django'),
        ('React', 'React'),
        ('JavaScript', 'JavaScript'),
        ('Machine Learning', 'Machine Learning'),
        ('SQL', 'SQL'),
        ('Java', 'Java'),
        ('C++', 'C++')
    ]
    for idx, (name, display) in enumerate(skills_list):
        SkillFilter.objects.get_or_create(name=name, defaults={'display_name': display, 'order': idx})

    print("Sample recruitment data successfully seeded!")
    print("\nAvailable User Logins for Testing:")
    print("1. Placement Cell Admin -> Username: admin | Password: admin123")
    print("2. Verified Recruiter (Infosys) -> Username: infosys_hr | Password: recruiter123")
    print("3. Verified Recruiter (TCS) -> Username: tcs_hr | Password: recruiter123")
    print("4. Pending Recruiter (Innovate AI) -> Username: innovate_hr | Password: recruiter123")
    print("5. Student 1 (Rahul Sharma) -> Username: rahul | Password: student123")
    print("6. Student 2 (Ananya Nair) -> Username: ananya | Password: student123")

if __name__ == '__main__':
    run_seed()
