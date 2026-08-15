from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Q, F, Count
from django.utils import timezone
from django.http import JsonResponse
import spacy

from .forms import (
    UserRegistrationForm, StudentProfileForm, SearchForm,
    RecruiterRegistrationForm, CompanyProfileForm, JobForm,
    JobApplicationForm, JobFilterForm
)
from .models import (
    Student, CompanyProfile, Job, JobApplication, SavedJob, JobView,
    Notification, RecruiterSearch, Analytics, SkillFilter
)
from .decorators import (
    approved_recruiter_required, recruiter_required,
    student_required, placement_admin_required
)
from .recommendations import calculate_job_match, get_recommended_jobs_for_student

# Define common words to exclude from analytics and popular searches
COMMON_WORDS = [
    'need', 'looking', 'for', 'with', 'and', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'of', 'is', 'are',
    'who', 'what', 'where', 'when', 'why', 'how', 'i', 'we', 'you', 'he', 'she', 'they', 'it', 'this', 'that',
    'these', 'those', 'am', 'can', 'will', 'should', 'would', 'could', 'may', 'might', 'must', 'have', 'has',
    'had', 'do', 'does', 'did', 'but', 'or', 'so', 'if', 'as', 'by', 'from', 'about', 'like', 'through', 'after',
    'before', 'between', 'under', 'over', 'into', 'during', 'until', 'while', 'against', 'because', 'without'
]

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


# ==========================================
# PUBLIC & TALENT DISCOVERY VIEWS
# ==========================================

def home(request):
    """Home landing page with hero, featured talent, active jobs summary, and role choices."""
    featured_students = Student.objects.exclude(user__is_staff=True)\
                                    .exclude(user__is_superuser=True)\
                                    .filter(skills__isnull=False, experience__isnull=False)\
                                    .select_related('user')\
                                    .order_by('-created_at')[:3]

    recent_jobs = Job.objects.filter(status='active', company__verification_status='approved', deadline__gt=timezone.now())\
                             .select_related('company')\
                             .order_by('-created_at')[:3]

    stats = {
        'total_students': Student.objects.exclude(user__is_staff=True).count(),
        'total_companies': CompanyProfile.objects.filter(verification_status='approved').count(),
        'active_jobs': Job.objects.filter(status='active', deadline__gt=timezone.now()).count(),
        'total_applications': JobApplication.objects.count()
    }

    context = {
        'featured_students': featured_students,
        'recent_jobs': recent_jobs,
        'stats': stats
    }
    return render(request, 'core/home.html', context)


def discover(request):
    """NLP Talent Search portal for recruiters and placement cell."""
    form = SearchForm(request.GET)
    students = Student.objects.exclude(user__is_staff=True).exclude(user__is_superuser=True).select_related('user')

    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        skills = form.cleaned_data.get('skills', '')
        location = form.cleaned_data.get('location', '')
        experience_level = form.cleaned_data.get('experience_level', '')
        sort_option = form.cleaned_data.get('sort', 'relevance')

        skill_mappings = {
            'teach': ['teacher', 'teaching', 'taught', 'education', 'instructor', 'tutor', 'lecturer', 'professor', 'mentor', 'coach', 'training'],
            'develop': ['developer', 'development', 'coding', 'programming', 'coder', 'engineer', 'software', 'web', 'app', 'application'],
            'frontend': ['front-end', 'front end', 'ui developer', 'javascript', 'react', 'angular', 'vue', 'html', 'css', 'web developer', 'client-side'],
            'backend': ['back-end', 'back end', 'server-side', 'api', 'database', 'server', 'python', 'java', 'php', 'node', 'express', 'django'],
            'fullstack': ['full-stack', 'full stack', 'end-to-end', 'frontend backend', 'front end back end'],
            'mobile': ['android', 'ios', 'swift', 'kotlin', 'react native', 'flutter', 'app developer', 'mobile app'],
            'design': ['designer', 'designing', 'graphic', 'ui', 'ux', 'user interface', 'user experience', 'creative'],
            'manage': ['manager', 'management', 'leadership', 'lead', 'project manager', 'product manager'],
            'write': ['writer', 'writing', 'content', 'copywriting', 'author', 'blog', 'article'],
            'market': ['marketer', 'marketing', 'digital marketing', 'seo', 'social media', 'advertising', 'growth'],
            'analyze': ['analyst', 'analysis', 'analytics', 'data', 'business intelligence', 'metrics', 'statistics'],
            'research': ['researcher', 'researching', 'study', 'investigation', 'r&d'],
            'consult': ['consultant', 'consulting', 'advisor', 'strategy', 'solutions'],
            'account': ['accountant', 'accounting', 'bookkeeping', 'finance', 'financial', 'tax'],
            'sell': ['sales', 'selling', 'salesperson', 'business development', 'account executive', 'revenue'],
            'assist': ['assistant', 'assisting', 'support', 'helping', 'customer service', 'administrative'],
            'administrate': ['administrator', 'administration', 'admin', 'operations', 'coordinator'],
            'coordinate': ['coordinator', 'coordinating', 'organization', 'planning', 'logistics'],
            'translate': ['translator', 'translation', 'language', 'interpreting', 'interpreter', 'localization'],
            'sport': ['sports', 'sportsman', 'sportswoman', 'athlete', 'athletic', 'football', 'soccer', 'basketball', 'baseball', 'tennis', 'golf', 'swimming', 'cricket', 'volleyball', 'rugby', 'hockey', 'fitness', 'coach', 'player', 'team', 'game', 'tournament', 'championship', 'league', 'match', 'competition'],
            'data': ['data science', 'data scientist', 'big data', 'data mining', 'data analysis', 'data analytics', 'data engineering', 'data engineer', 'database', 'sql', 'nosql', 'hadoop', 'spark', 'data visualization', 'machine learning', 'ml', 'ai', 'artificial intelligence', 'statistics', 'statistical analysis', 'data modeling', 'etl', 'data pipeline', 'data warehouse', 'data lake', 'business intelligence', 'bi'],
            'excel': ['microsoft excel', 'spreadsheet', 'pivot tables', 'vlookup', 'hlookup', 'excel formulas', 'excel functions', 'macros', 'vba', 'data analysis', 'data modeling', 'excel dashboard', 'excel reporting', 'data visualization', 'data entry', 'data management', 'excel automation'],
            'powerbi': ['power bi', 'power bi desktop', 'power bi service', 'dax', 'power query', 'm language', 'bi', 'business intelligence', 'data visualization', 'dashboard', 'reporting', 'data modeling', 'data analysis', 'microsoft bi', 'power bi report server'],
            'tableau': ['tableau desktop', 'tableau server', 'tableau online', 'tableau prep', 'data visualization', 'dashboard', 'reporting', 'bi', 'business intelligence', 'data analysis', 'tableau public', 'visual analytics'],
            'visualization': ['data visualization', 'dashboard', 'chart', 'graph', 'infographic', 'reporting', 'visual analytics', 'data storytelling', 'bi', 'business intelligence', 'd3.js', 'plotly', 'grafana', 'kibana', 'matplotlib', 'seaborn', 'ggplot2', 'bokeh', 'highcharts', 'chart.js'],
            'sql': ['structured query language', 'database', 'query', 'mysql', 'postgresql', 'sql server', 'oracle', 'sqlite', 'data analysis', 'data extraction', 'data manipulation', 'joins', 'stored procedures', 'triggers', 'database design', 'database management', 'data modeling'],
            'python': ['pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'tensorflow', 'pytorch', 'data analysis', 'data science', 'machine learning', 'data visualization', 'jupyter notebook', 'jupyter lab', 'python programming', 'data manipulation', 'data cleaning'],
            'r': ['r programming', 'r studio', 'ggplot2', 'dplyr', 'tidyr', 'shiny', 'r markdown', 'statistical analysis', 'data visualization', 'data science', 'statistical computing', 'data modeling', 'statistical graphics'],
            'statistics': ['statistical analysis', 'hypothesis testing', 'regression analysis', 'time series analysis', 'a/b testing', 'anova', 'factor analysis', 'cluster analysis', 'bayesian statistics', 'predictive modeling', 'forecasting', 'statistical inference', 'probability', 'descriptive statistics', 'inferential statistics'],
            'bi': ['business intelligence', 'bi tools', 'dashboard', 'reporting', 'kpi', 'metrics', 'data analysis', 'data visualization', 'decision support', 'olap', 'data warehouse', 'etl', 'business analytics', 'performance analytics', 'data-driven decision making'],
            'analytics': ['data analytics', 'web analytics', 'google analytics', 'marketing analytics', 'predictive analytics', 'prescriptive analytics', 'descriptive analytics', 'diagnostic analytics', 'business analytics', 'customer analytics', 'social media analytics', 'analytics tools', 'analytics platform', 'analytics dashboard'],
            'bigdata': ['hadoop', 'spark', 'hive', 'pig', 'kafka', 'cassandra', 'mongodb', 'nosql', 'data lake', 'data warehouse', 'distributed computing', 'mapreduce', 'big data processing', 'big data analytics', 'data engineering', 'data pipeline', 'data architecture'],
            'cloud': ['cloud computing', 'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud', 'cloud architect', 'cloud engineer', 'devops', 'infrastructure', 'iaas', 'paas', 'saas', 'serverless', 'docker', 'kubernetes', 'container', 'microservices', 'cloud migration', 'cloud security', 'cloud storage', 'cloud database', 'snowflake', 'redshift', 'bigquery', 'azure synapse', 'databricks']
        }

        if query and nlp:
            doc = nlp(query.lower())
            keywords = []
            lemmas = []
            for token in doc:
                if not token.is_stop and not token.is_punct and len(token.text) > 2:
                    keywords.append(token.text)
                    lemmas.append(token.lemma_)

            expanded_keywords = set(keywords + lemmas)
            for lemma in lemmas:
                if lemma in skill_mappings:
                    expanded_keywords.update(skill_mappings[lemma])
                for key, values in skill_mappings.items():
                    if lemma in values or any(lemma in value for value in values):
                        expanded_keywords.update([key] + values)

            if 'frontend' in query.lower() or 'front-end' in query.lower() or 'front end' in query.lower():
                expanded_keywords.update(skill_mappings['frontend'])

            if 'backend' in query.lower() or 'back-end' in query.lower() or 'back end' in query.lower():
                expanded_keywords.update(skill_mappings['backend'])

            q_objects = Q()
            for keyword in expanded_keywords:
                q_objects |= (
                    Q(skills__icontains=keyword) |
                    Q(experience__icontains=keyword) |
                    Q(projects__icontains=keyword) |
                    Q(department__icontains=keyword) |
                    Q(course__icontains=keyword)
                )
            students = students.filter(q_objects)

            RecruiterSearch.objects.create(
                search_query=query,
                filters_used={'skills': skills, 'location': location, 'experience_level': experience_level}
            )

            for keyword in keywords:
                if keyword.lower() in COMMON_WORDS or len(keyword) < 3:
                    continue
                try:
                    analytics = Analytics.objects.get(skill_name=keyword)
                    analytics.search_count = F('search_count') + 1
                    analytics.save()
                except Analytics.DoesNotExist:
                    Analytics.objects.create(skill_name=keyword, search_count=1)

        if skills:
            skill_list = [s.strip() for s in skills.split(',') if s.strip()]
            if skill_list and nlp:
                skill_query = Q()
                expanded_skills = set()
                for skill in skill_list:
                    expanded_skills.add(skill)
                    skill_doc = nlp(skill.lower())
                    for token in skill_doc:
                        if not token.is_stop and not token.is_punct:
                            expanded_skills.add(token.lemma_)
                            if token.lemma_ in skill_mappings:
                                expanded_skills.update(skill_mappings[token.lemma_])
                for skill in expanded_skills:
                    skill_query |= Q(skills__icontains=skill)
                students = students.filter(skill_query)

        if location:
            location_list = [loc.strip() for loc in location.split(',') if loc.strip()]
            if location_list:
                location_query = Q()
                for loc in location_list:
                    location_query |= Q(experience__icontains=loc)
                students = students.filter(location_query)

        if experience_level:
            students = students.filter(experience__icontains=experience_level)

    popular_searches = Analytics.objects.exclude(skill_name__in=COMMON_WORDS).order_by('-search_count')[:5]
    skill_filters = SkillFilter.objects.filter(is_active=True).order_by('order', 'name')

    if form.is_valid():
        sort_option = form.cleaned_data.get('sort', 'relevance')
        if sort_option == 'recent':
            students = students.order_by('-created_at')
        else:
            students = students.order_by('-created_at')
    else:
        students = students.order_by('-created_at')

    context = {
        'form': form,
        'students': students,
        'total_results': students.count(),
        'popular_searches': popular_searches,
        'skill_filters': skill_filters,
        'current_sort': sort_option if form.is_valid() else 'relevance'
    }
    return render(request, 'core/discover.html', context)


# ==========================================
# AUTHENTICATION & STUDENT PROFILE VIEWS
# ==========================================

def register(request):
    """Student user registration."""
    if request.user.is_authenticated:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                Student.objects.create(user=user)
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to ASIET Talent Hub. Please complete your profile.')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def profile(request):
    """View and update student profile with academic & contact details and profile picture management."""
    student, _ = Student.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                # Update User first/last name
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.save()

                student_obj = form.save(commit=False)

                # Check if remove profile picture checkbox was checked
                if form.cleaned_data.get('remove_profile_picture'):
                    if student_obj.profile_picture:
                        student_obj.profile_picture.delete(save=False)
                    student_obj.profile_picture = None

                student_obj.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = StudentProfileForm(instance=student, initial=initial_data)

    completion_percentage = student.get_profile_completion_percentage()

    context = {
        'form': form,
        'student': student,
        'completion_percentage': completion_percentage
    }
    return render(request, 'core/profile.html', context)


@login_required
def delete_profile(request):
    """Delete student account and profile."""
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        user = request.user
        student.delete()
        user.delete()
        messages.success(request, 'Your profile has been deleted.')
        return redirect('home')
    return render(request, 'core/delete_profile.html')


# ==========================================
# RECRUITER / COMPANY VIEWS
# ==========================================

def recruiter_register(request):
    """Recruiter & Company Registration view."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'company_profile'):
            return redirect('recruiter_dashboard')
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = RecruiterRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create User account for Recruiter
                official_email = form.cleaned_data['official_email']
                username_base = official_email.split('@')[0]
                username = username_base
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}_{counter}"
                    counter += 1

                names = form.cleaned_data['hr_name'].split(' ', 1)
                first_name = names[0]
                last_name = names[1] if len(names) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=official_email,
                    password=form.cleaned_data['password1'],
                    first_name=first_name,
                    last_name=last_name
                )

                # Create CompanyProfile linked to user with pending status
                CompanyProfile.objects.create(
                    user=user,
                    company_name=form.cleaned_data['company_name'],
                    hr_name=form.cleaned_data['hr_name'],
                    official_email=official_email,
                    phone_number=form.cleaned_data['phone_number'],
                    website=form.cleaned_data.get('website'),
                    location=form.cleaned_data['location'],
                    industry=form.cleaned_data['industry'],
                    description=form.cleaned_data['description'],
                    logo=form.cleaned_data.get('logo'),
                    linkedin_url=form.cleaned_data.get('linkedin_url'),
                    verification_status='pending'
                )

                # Notify Placement Cell Admins
                admins = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
                for admin_user in admins:
                    Notification.objects.create(
                        recipient=admin_user,
                        notification_type='recruiter_verification',
                        title='New Recruiter Verification Request',
                        message=f"{form.cleaned_data['company_name']} ({form.cleaned_data['hr_name']}) has registered and requires verification."
                    )

                login(request, user)
                messages.info(
                    request,
                    'Company registration submitted successfully! Your account is currently under verification by the ASIET Placement Cell.'
                )
                return redirect('recruiter_pending')
            except Exception as e:
                messages.error(request, f'Company registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RecruiterRegistrationForm()
    return render(request, 'core/recruiter/register.html', {'form': form})


@recruiter_required
def recruiter_pending(request):
    """Display pending verification message for unverified recruiters."""
    company = request.user.company_profile
    if company.verification_status == 'approved':
        return redirect('recruiter_dashboard')
    return render(request, 'core/recruiter/pending.html', {'company': company})


@approved_recruiter_required
def recruiter_dashboard(request):
    """Dashboard for approved recruiters with metrics, recent applications, and posted jobs."""
    company = request.user.company_profile
    now = timezone.now()

    jobs = Job.objects.filter(company=company)
    active_jobs = jobs.filter(status='active', deadline__gt=now)
    closed_jobs = jobs.filter(Q(status='closed') | Q(deadline__lte=now))

    applications = JobApplication.objects.filter(job__company=company).select_related('student__user', 'job')
    shortlisted_count = applications.filter(status__in=['shortlisted', 'interview_scheduled', 'selected']).count()

    recent_applications = applications[:8]
    recent_applications_with_scores = []
    for app in recent_applications:
        match_info = calculate_job_match(app.student, app.job)
        recent_applications_with_scores.append({
            'application': app,
            'match_score': match_info['match_score']
        })

    metrics = {
        'active_jobs': active_jobs.count(),
        'total_applications': applications.count(),
        'shortlisted_candidates': shortlisted_count,
        'closed_jobs': closed_jobs.count(),
    }

    context = {
        'company': company,
        'metrics': metrics,
        'jobs': jobs,
        'recent_applications': recent_applications_with_scores
    }
    return render(request, 'core/recruiter/dashboard.html', context)


@recruiter_required
def recruiter_company_profile(request):
    """View and update recruiter's company profile."""
    company = request.user.company_profile
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company profile updated successfully!')
            return redirect('recruiter_company_profile')
    else:
        form = CompanyProfileForm(instance=company)
    return render(request, 'core/recruiter/company_profile.html', {'form': form, 'company': company})


@approved_recruiter_required
def job_create(request):
    """Create a new job or internship opportunity."""
    company = request.user.company_profile
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.posted_by = request.user
            job.save()

            messages.success(request, f'Opportunity "{job.title}" created successfully!')
            return redirect('recruiter_dashboard')
        else:
            messages.error(request, 'Please fix the errors in the form.')
    else:
        form = JobForm()
    return render(request, 'core/recruiter/job_form.html', {'form': form, 'action': 'Create'})


@approved_recruiter_required
def job_edit(request, job_id):
    """Edit an existing job (verifying company ownership)."""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=job_id, company=company)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job "{job.title}" updated successfully!')
            return redirect('recruiter_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'core/recruiter/job_form.html', {'form': form, 'job': job, 'action': 'Edit'})


@approved_recruiter_required
def job_toggle_status(request, job_id):
    """Close or re-open a job."""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=job_id, company=company)

    if job.status == 'active':
        job.status = 'closed'
        messages.info(request, f'Job "{job.title}" has been closed.')
    else:
        job.status = 'active'
        messages.success(request, f'Job "{job.title}" is now active.')
    job.save()
    return redirect('recruiter_dashboard')


@approved_recruiter_required
def job_delete(request, job_id):
    """Delete a job posting."""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=job_id, company=company)
    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'Job "{title}" deleted successfully.')
        return redirect('recruiter_dashboard')
    return render(request, 'core/recruiter/job_confirm_delete.html', {'job': job})


@approved_recruiter_required
def job_applicants(request, job_id):
    """View and evaluate applicants for a specific job (company ownership verified)."""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=job_id, company=company)

    applications = JobApplication.objects.filter(job=job).select_related('student__user')

    # Filter status if requested
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)

    applicant_list = []
    for app in applications:
        match_info = calculate_job_match(app.student, job)
        applicant_list.append({
            'application': app,
            'student': app.student,
            'match_info': match_info,
            'match_score': match_info['match_score']
        })

    # Sort applicants by match score by default
    applicant_list.sort(key=lambda x: x['match_score'], reverse=True)

    context = {
        'job': job,
        'applicant_list': applicant_list,
        'total_applicants': len(applicant_list),
        'current_status_filter': status_filter
    }
    return render(request, 'core/recruiter/job_applicants.html', context)


@approved_recruiter_required
def update_application_status(request, application_id):
    """Update applicant status (Shortlist, Reject, Select, etc.) and notify student."""
    company = request.user.company_profile
    application = get_object_or_404(JobApplication, pk=application_id, job__company=company)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
        if new_status in valid_statuses:
            application.status = new_status
            application.save()

            # Create Notification for student
            status_display = dict(JobApplication.STATUS_CHOICES).get(new_status, new_status)
            Notification.objects.create(
                recipient=application.student.user,
                notification_type='status_update',
                title=f'Application Status Update: {application.job.title}',
                message=f'Your application for {application.job.title} at {company.company_name} has been updated to: {status_display}.',
                related_job=application.job
            )

            messages.success(request, f'Status for {application.student.user.get_full_name()} updated to {status_display}.')
        else:
            messages.error(request, 'Invalid status choice.')

    return redirect('job_applicants', job_id=application.job.id)


# ==========================================
# STUDENT JOBS & APPLICATION VIEWS
# ==========================================

@student_required
def student_dashboard(request):
    """Student Dashboard with profile completion, AI recommendations, applications, and saved jobs."""
    student, _ = Student.objects.get_or_create(user=request.user)

    completion_pct = student.get_profile_completion_percentage()
    recommendations = get_recommended_jobs_for_student(student, limit=6)

    my_applications = JobApplication.objects.filter(student=student).select_related('job__company')
    saved_jobs = SavedJob.objects.filter(student=student).select_related('job__company')

    app_metrics = {
        'applied': my_applications.filter(status='applied').count(),
        'under_review': my_applications.filter(status='under_review').count(),
        'shortlisted': my_applications.filter(status__in=['shortlisted', 'interview_scheduled']).count(),
        'selected': my_applications.filter(status='selected').count(),
    }

    context = {
        'student': student,
        'completion_pct': completion_pct,
        'recommendations': recommendations,
        'recent_applications': my_applications[:5],
        'saved_jobs': saved_jobs[:5],
        'app_metrics': app_metrics
    }
    return render(request, 'core/student/dashboard.html', context)


def job_list(request):
    """Browse & Search all active job and internship postings."""
    form = JobFilterForm(request.GET)
    now = timezone.now()

    jobs = Job.objects.filter(status='active', company__verification_status='approved', deadline__gt=now)\
                      .select_related('company')

    if form.is_valid():
        query = form.cleaned_data.get('query')
        opportunity_type = form.cleaned_data.get('opportunity_type')
        work_mode = form.cleaned_data.get('work_mode')
        department = form.cleaned_data.get('department')

        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(required_skills__icontains=query) |
                Q(company__company_name__icontains=query)
            )

        if opportunity_type:
            jobs = jobs.filter(opportunity_type=opportunity_type)

        if work_mode:
            jobs = jobs.filter(work_mode=work_mode)

        if department:
            jobs = jobs.filter(
                Q(eligible_departments__icontains=department) |
                Q(eligible_departments='')
            )

    job_list_with_scores = []
    student = None
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile

    for job in jobs:
        match_score = None
        if student:
            match_info = calculate_job_match(student, job)
            match_score = match_info['match_score']

        job_list_with_scores.append({
            'job': job,
            'match_score': match_score
        })

    if student and request.GET.get('sort') == 'match':
        job_list_with_scores.sort(key=lambda x: x['match_score'] or 0, reverse=True)

    context = {
        'form': form,
        'job_list': job_list_with_scores,
        'total_jobs': len(job_list_with_scores)
    }
    return render(request, 'core/student/job_list.html', context)


def job_detail(request, job_id):
    """View complete details of a job opportunity, with AI match score breakdown for students."""
    job = get_object_or_404(Job, pk=job_id, company__verification_status='approved')

    match_info = None
    has_applied = False
    has_saved = False
    student = None

    if request.user.is_authenticated and not hasattr(request.user, 'company_profile') and not request.user.is_staff:
        student, _ = Student.objects.get_or_create(user=request.user)
        match_info = calculate_job_match(student, job)

        has_applied = JobApplication.objects.filter(student=student, job=job).exists()
        has_saved = SavedJob.objects.filter(student=student, job=job).exists()

        # Record JobView
        JobView.objects.create(student=student, job=job)

    context = {
        'job': job,
        'match_info': match_info,
        'has_applied': has_applied,
        'has_saved': has_saved,
        'student': student
    }
    return render(request, 'core/student/job_detail.html', context)


@student_required
def job_apply(request, job_id):
    """Submit application for a job opportunity."""
    student = request.user.student_profile
    job = get_object_or_404(Job, pk=job_id)

    if not job.is_accepting_applications():
        messages.error(request, 'This opportunity is no longer accepting applications.')
        return redirect('job_detail', job_id=job.id)

    if JobApplication.objects.filter(student=student, job=job).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.job = job

            # Use custom resume if provided, otherwise student profile resume
            custom_resume = form.cleaned_data.get('custom_resume')
            if custom_resume:
                application.resume = custom_resume
            elif student.resume:
                application.resume = student.resume

            application.save()

            # Notify recruiter
            Notification.objects.create(
                recipient=job.posted_by,
                notification_type='job_application',
                title=f'New Application for {job.title}',
                message=f'{student.user.get_full_name()} has applied for {job.title}.',
                related_job=job
            )

            messages.success(request, 'Application submitted successfully!')
            return redirect('student_applications')
    else:
        form = JobApplicationForm()

    match_info = calculate_job_match(student, job)

    context = {
        'job': job,
        'student': student,
        'form': form,
        'match_info': match_info
    }
    return render(request, 'core/student/job_apply.html', context)


@student_required
def job_save_toggle(request, job_id):
    """Bookmark or remove bookmark for a job."""
    student = request.user.student_profile
    job = get_object_or_404(Job, pk=job_id)

    saved_item = SavedJob.objects.filter(student=student, job=job).first()
    if saved_item:
        saved_item.delete()
        messages.info(request, f'Removed "{job.title}" from saved jobs.')
    else:
        SavedJob.objects.create(student=student, job=job)
        messages.success(request, f'Saved "{job.title}" to your bookmarks.')

    next_url = request.META.get('HTTP_REFERER') or redirect('job_detail', job_id=job.id).url
    return redirect(next_url)


@student_required
def student_applications(request):
    """Track student's submitted applications and status."""
    student = request.user.student_profile
    applications = JobApplication.objects.filter(student=student).select_related('job__company')

    application_list = []
    for app in applications:
        match_info = calculate_job_match(student, app.job)
        application_list.append({
            'application': app,
            'match_score': match_info['match_score']
        })

    return render(request, 'core/student/applications.html', {'application_list': application_list})


@student_required
def withdraw_application(request, application_id):
    """Withdraw a job application."""
    student = request.user.student_profile
    application = get_object_or_404(JobApplication, pk=application_id, student=student)

    if request.method == 'POST':
        application.status = 'withdrawn'
        application.save()
        messages.info(request, f'Application for "{application.job.title}" withdrawn.')
        return redirect('student_applications')

    return render(request, 'core/student/confirm_withdraw.html', {'application': application})


# ==========================================
# ADMIN / PLACEMENT CELL VIEWS
# ==========================================

@placement_admin_required
def placement_admin_dashboard(request):
    """Redirect Placement Cell Administration to standard Django Admin control center."""
    return redirect('admin:index')



# ==========================================
# NOTIFICATIONS VIEWS
# ==========================================

@login_required
def notifications_list(request):
    """View all in-app notifications for the logged in user."""
    notifications = Notification.objects.filter(recipient=request.user)

    # Mark all as read on viewing page
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'core/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})
