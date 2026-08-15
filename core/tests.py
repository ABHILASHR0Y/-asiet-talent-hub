from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from core.models import Student, CompanyProfile, Job, JobApplication, SavedJob, Notification
from core.recommendations import calculate_job_match, get_recommended_jobs_for_student


class RecruitmentPlatformWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin user
        self.admin_user = User.objects.create_superuser(
            username='placement_admin',
            email='admin@asiet.edu.in',
            password='AdminPassword123!'
        )

        # Student user
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@asiet.edu.in',
            password='StudentPassword123!',
            first_name='Rahul',
            last_name='Sharma'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            course='B.Tech',
            department='Computer Science',
            cgpa=Decimal('8.50'),
            graduation_year=2026,
            skills='Python, Django, MySQL, React',
            experience='Web developer intern at TechCorp',
            projects='ASIET Talent Hub platform'
        )

        # Second Student
        self.student_user2 = User.objects.create_user(
            username='student2',
            email='student2@asiet.edu.in',
            password='StudentPassword123!',
            first_name='Ananya',
            last_name='Nair'
        )
        self.student2 = Student.objects.create(
            user=self.student_user2,
            course='B.Tech',
            department='Electronics',
            cgpa=Decimal('6.50'),
            skills='C++, Embedded Systems'
        )

    def test_01_recruiter_registration_pending_status(self):
        """TEST 1: Company registers -> account becomes Pending."""
        response = self.client.post('/recruiter/register/', {
            'company_name': 'TechCorp Solutions',
            'hr_name': 'Sarah Connor',
            'official_email': 'hr@techcorp.com',
            'phone_number': '+91 9876543210',
            'website': 'https://techcorp.com',
            'location': 'Kochi, India',
            'industry': 'Software',
            'description': 'Leading software development firm',
            'password1': 'RecruiterPass123!',
            'password2': 'RecruiterPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CompanyProfile.objects.filter(company_name='TechCorp Solutions').exists())
        company = CompanyProfile.objects.get(company_name='TechCorp Solutions')
        self.assertEqual(company.verification_status, 'pending')

    def test_02_pending_recruiter_blocked_from_posting_jobs(self):
        """TEST 2: Pending recruiter attempts to post job -> access denied (redirected to pending)."""
        recruiter_user = User.objects.create_user(username='pending_hr', email='hr@pending.com', password='pass')
        CompanyProfile.objects.create(
            user=recruiter_user, company_name='Pending Inc', hr_name='HR',
            official_email='hr@pending.com', phone_number='123', location='Kochi',
            industry='IT', description='Desc', verification_status='pending'
        )
        self.client.login(username='pending_hr', password='pass')
        response = self.client.get('/recruiter/jobs/create/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/recruiter/pending/', response.url)

    def test_03_admin_approves_recruiter(self):
        """TEST 3: Admin approves recruiter -> recruiter receives approved status."""
        recruiter_user = User.objects.create_user(username='hr_app', email='hr@app.com', password='pass')
        company = CompanyProfile.objects.create(
            user=recruiter_user, company_name='Approve Inc', hr_name='HR',
            official_email='hr@app.com', phone_number='123', location='Kochi',
            industry='IT', description='Desc', verification_status='pending'
        )
        company.verification_status = 'approved'
        company.verified_by = self.admin_user
        company.verified_at = timezone.now()
        company.save()

        company.refresh_from_db()
        self.assertEqual(company.verification_status, 'approved')
        self.assertEqual(company.verified_by, self.admin_user)

    def test_04_approved_recruiter_creates_job(self):
        """TEST 4: Approved recruiter creates and publishes job."""
        recruiter_user = User.objects.create_user(username='approved_hr', email='hr@approved.com', password='pass')
        company = CompanyProfile.objects.create(
            user=recruiter_user, company_name='Approved Corp', hr_name='HR',
            official_email='hr@approved.com', phone_number='123', location='Kochi',
            industry='IT', description='Desc', verification_status='approved'
        )
        self.client.login(username='approved_hr', password='pass')
        deadline = timezone.now() + timedelta(days=14)
        response = self.client.post('/recruiter/jobs/create/', {
            'title': 'Python Developer Intern',
            'opportunity_type': 'internship',
            'work_mode': 'on_site',
            'location': 'Kochi',
            'description': 'Develop backend apps in Python and Django',
            'required_skills': 'Python, Django, MySQL',
            'preferred_skills': 'React',
            'eligible_departments': 'Computer Science',
            'minimum_cgpa': '7.5',
            'graduation_year': '2026',
            'experience_required': 'Freshers',
            'salary_or_stipend': '₹25,000 / month',
            'openings': '3',
            'deadline': deadline.strftime('%Y-%m-%dT%H:%M'),
            'selection_process': '1. Test -> 2. Interview',
            'status': 'active'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Job.objects.filter(title='Python Developer Intern').exists())

    def test_05_job_appears_for_eligible_students(self):
        """TEST 5: Job appears for eligible students on jobs portal."""
        recruiter_user = User.objects.create_user(username='hr_job5', email='hr5@test.com', password='pass')
        company = CompanyProfile.objects.create(
            user=recruiter_user, company_name='Test Comp 5', hr_name='HR',
            official_email='hr5@test.com', phone_number='123', location='Kochi',
            industry='IT', description='Desc', verification_status='approved'
        )
        job = Job.objects.create(
            company=company, posted_by=recruiter_user, title='Frontend Developer',
            opportunity_type='full_time', work_mode='remote', location='Kochi',
            description='React dev', required_skills='React, JavaScript',
            salary_or_stipend='₹6 LPA', openings=2, deadline=timezone.now() + timedelta(days=10),
            status='active'
        )
        response = self.client.get('/jobs/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Frontend Developer')

    def test_06_recommendation_and_match_score(self):
        """TEST 6: Student receives appropriate recommendation and explainable match score."""
        recruiter_user = User.objects.create_user(username='hr_rec', email='hrrec@test.com', password='pass')
        company = CompanyProfile.objects.create(
            user=recruiter_user, company_name='AI Tech', hr_name='HR',
            official_email='hrrec@test.com', phone_number='123', location='Kochi',
            industry='IT', description='Desc', verification_status='approved'
        )
        job = Job.objects.create(
            company=company, posted_by=recruiter_user, title='Python Backend Engineer',
            opportunity_type='full_time', work_mode='on_site', location='Kochi',
            description='Build Django APIs', required_skills='Python, Django, MySQL',
            eligible_departments='Computer Science', minimum_cgpa=Decimal('7.5'),
            salary_or_stipend='₹8 LPA', openings=1, deadline=timezone.now() + timedelta(days=10),
            status='active'
        )
        match_info = calculate_job_match(self.student, job)
        self.assertGreaterEqual(match_info['match_score'], 80)
        self.assertTrue(match_info['dept_eligible'])
        self.assertTrue(match_info['cgpa_eligible'])

    def test_07_and_08_student_apply_and_duplicate_prevention(self):
        """TEST 7 & TEST 8: Student applies, and duplicate application is blocked."""
        recruiter_user = User.objects.create_user(username='hr_app7', email='hrapp7@test.com', password='pass')
        company = CompanyProfile.objects.create(
            user=recruiter_user, company_name='Apply Corp', hr_name='HR',
            official_email='hrapp7@test.com', phone_number='123', location='Kochi',
            industry='IT', description='Desc', verification_status='approved'
        )
        job = Job.objects.create(
            company=company, posted_by=recruiter_user, title='Fullstack Developer',
            opportunity_type='full_time', work_mode='hybrid', location='Kochi',
            description='Fullstack dev', required_skills='Python, React',
            salary_or_stipend='₹7 LPA', openings=2, deadline=timezone.now() + timedelta(days=10),
            status='active'
        )
        self.client.login(username='student1', password='StudentPassword123!')

        # First Apply
        response = self.client.post(f'/jobs/{job.id}/apply/', {'cover_note': 'Super excited for this role!'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(JobApplication.objects.filter(student=self.student, job=job).exists())

        # Second Apply (Duplicate check)
        response_dup = self.client.post(f'/jobs/{job.id}/apply/', {'cover_note': 'Duplicate submission'})
        self.assertEqual(response_dup.status_code, 302)
        self.assertEqual(JobApplication.objects.filter(student=self.student, job=job).count(), 1)

    def test_09_10_11_recruiter_applicant_review_and_status_update(self):
        """TEST 9, 10, 11: Recruiter views application, shortlists candidate, student sees updated status."""
        recruiter_user = User.objects.create_user(username='hr_rev', email='hrrev@test.com', password='pass')
        company = CompanyProfile.objects.create(
            user=recruiter_user, company_name='Review Corp', hr_name='HR',
            official_email='hrrev@test.com', phone_number='123', location='Kochi',
            industry='IT', description='Desc', verification_status='approved'
        )
        job = Job.objects.create(
            company=company, posted_by=recruiter_user, title='Software Engineer',
            opportunity_type='full_time', work_mode='on_site', location='Kochi',
            description='Dev', required_skills='Python',
            salary_or_stipend='₹6 LPA', openings=1, deadline=timezone.now() + timedelta(days=10),
            status='active'
        )
        application = JobApplication.objects.create(student=self.student, job=job, status='applied')

        # Recruiter views applicants
        self.client.login(username='hr_rev', password='pass')
        response_view = self.client.get(f'/recruiter/jobs/{job.id}/applicants/')
        self.assertEqual(response_view.status_code, 200)

        # Recruiter shortlists candidate
        response_shortlist = self.client.post(f'/recruiter/applications/{application.id}/status/', {
            'status': 'shortlisted'
        })
        self.assertEqual(response_shortlist.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, 'shortlisted')

        # Student checks status
        self.client.login(username='student1', password='StudentPassword123!')
        response_student = self.client.get('/student/applications/')
        self.assertEqual(response_student.status_code, 200)
        self.assertContains(response_student, 'Shortlisted')

    def test_13_recruiter_authorization_isolation(self):
        """TEST 13: Recruiter cannot access another company's applicants."""
        user1 = User.objects.create_user(username='hr1', email='hr1@test.com', password='pass')
        company1 = CompanyProfile.objects.create(user=user1, company_name='Comp 1', hr_name='HR1', official_email='hr1@test.com', phone_number='1', location='L', industry='I', description='D', verification_status='approved')
        job1 = Job.objects.create(company=company1, posted_by=user1, title='Job 1', opportunity_type='full_time', work_mode='on_site', location='L', description='D', required_skills='S', salary_or_stipend='S', openings=1, deadline=timezone.now() + timedelta(days=10), status='active')

        user2 = User.objects.create_user(username='hr2', email='hr2@test.com', password='pass')
        company2 = CompanyProfile.objects.create(user=user2, company_name='Comp 2', hr_name='HR2', official_email='hr2@test.com', phone_number='2', location='L', industry='I', description='D', verification_status='approved')

        # Recruiter 2 tries to access Recruiter 1's job applicants -> 404
        self.client.login(username='hr2', password='pass')
        response = self.client.get(f'/recruiter/jobs/{job1.id}/applicants/')
        self.assertEqual(response.status_code, 404)

    def test_14_student_cannot_access_admin_or_recruiter_pages(self):
        """TEST 14: Student cannot access recruiter/admin pages."""
        self.client.login(username='student1', password='StudentPassword123!')

        response_admin = self.client.get('/placement-admin/')
        self.assertEqual(response_admin.status_code, 302)

        response_recruiter = self.client.get('/recruiter/dashboard/')
        self.assertEqual(response_recruiter.status_code, 302)

    def test_15_expired_job_cannot_accept_applications(self):
        """TEST 15: Expired job cannot accept applications."""
        recruiter_user = User.objects.create_user(username='hr_exp', email='hrexp@test.com', password='pass')
        company = CompanyProfile.objects.create(user=recruiter_user, company_name='Exp Corp', hr_name='HR', official_email='hrexp@test.com', phone_number='1', location='L', industry='I', description='D', verification_status='approved')
        expired_job = Job.objects.create(
            company=company, posted_by=recruiter_user, title='Old Job',
            opportunity_type='full_time', work_mode='on_site', location='L',
            description='Desc', required_skills='Python', salary_or_stipend='S', openings=1,
            deadline=timezone.now() - timedelta(days=2), status='active'
        )
        self.client.login(username='student1', password='StudentPassword123!')
        response = self.client.post(f'/jobs/{expired_job.id}/apply/', {'cover_note': 'Late apply'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(JobApplication.objects.filter(student=self.student, job=expired_job).exists())

    def test_16_suspended_recruiter_functions_blocked(self):
        """TEST 16: Admin suspends recruiter -> restricted recruiter functions are blocked."""
        recruiter_user = User.objects.create_user(username='hr_susp', email='hrsusp@test.com', password='pass')
        company = CompanyProfile.objects.create(user=recruiter_user, company_name='Susp Corp', hr_name='HR', official_email='hrsusp@test.com', phone_number='1', location='L', industry='I', description='D', verification_status='suspended')
        self.client.login(username='hr_susp', password='pass')
        response = self.client.get('/recruiter/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/recruiter/pending/', response.url)
