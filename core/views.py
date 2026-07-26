from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Q, F
import spacy
from .forms import UserRegistrationForm, StudentProfileForm, SearchForm
from .models import Student, RecruiterSearch, Analytics, SkillFilter

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
except:
    nlp = None

def home(request):
    # Get featured students (excluding admin accounts)
    featured_students = Student.objects.exclude(user__is_staff=True)\
                                    .exclude(user__is_superuser=True)\
                                    .filter(skills__isnull=False, experience__isnull=False)\
                                    .order_by('-created_at')[:3]  # Get the 3 most recent profiles

    return render(request, 'core/home.html', {'featured_students': featured_students})

def discover(request):
    form = SearchForm(request.GET)
    # Exclude students with admin accounts (is_staff or is_superuser)
    students = Student.objects.exclude(user__is_staff=True).exclude(user__is_superuser=True)

    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        skills = form.cleaned_data.get('skills', '')
        location = form.cleaned_data.get('location', '')
        experience_level = form.cleaned_data.get('experience_level', '')
        sort_option = form.cleaned_data.get('sort', 'relevance')  # Default to relevance

        # Define common skill-related word mappings (e.g., teacher -> teaching)
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
            # Sports-related mappings
            'sport': ['sports', 'sportsman', 'sportswoman', 'athlete', 'athletic', 'football', 'soccer', 'basketball', 'baseball', 'tennis', 'golf', 'swimming', 'cricket', 'volleyball', 'rugby', 'hockey', 'fitness', 'coach', 'player', 'team', 'game', 'tournament', 'championship', 'league', 'match', 'competition'],
            # Data Analytics mappings
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
            # Process the natural language query
            doc = nlp(query.lower())

            # Extract relevant keywords and their lemmas (base forms)
            keywords = []
            lemmas = []
            for token in doc:
                if not token.is_stop and not token.is_punct and len(token.text) > 2:
                    keywords.append(token.text)
                    lemmas.append(token.lemma_)

            # Add related terms based on lemmas
            expanded_keywords = set(keywords + lemmas)
            for lemma in lemmas:
                if lemma in skill_mappings:
                    expanded_keywords.update(skill_mappings[lemma])
                # Also check if any mapping key contains this lemma
                for key, values in skill_mappings.items():
                    if lemma in values or any(lemma in value for value in values):
                        expanded_keywords.update([key] + values)

            # Special case for frontend/backend developers
            if 'frontend' in query.lower() or 'front-end' in query.lower() or 'front end' in query.lower():
                expanded_keywords.update(skill_mappings['frontend'])
                expanded_keywords.add('frontend')
                expanded_keywords.add('front-end')
                expanded_keywords.add('front end')

            if 'backend' in query.lower() or 'back-end' in query.lower() or 'back end' in query.lower():
                expanded_keywords.update(skill_mappings['backend'])
                expanded_keywords.add('backend')
                expanded_keywords.add('back-end')
                expanded_keywords.add('back end')

            # Special case for sports-related terms
            if 'sport' in query.lower() or 'sportsman' in query.lower() or 'athlete' in query.lower():
                expanded_keywords.update(skill_mappings['sport'])
                expanded_keywords.add('sport')
                expanded_keywords.add('sports')
                expanded_keywords.add('sportsman')
                expanded_keywords.add('athlete')

            # Special case for data analytics terms
            if 'data' in query.lower() or 'analytics' in query.lower() or 'analyst' in query.lower():
                expanded_keywords.update(skill_mappings['data'])
                expanded_keywords.update(skill_mappings['analytics'])
                expanded_keywords.update(skill_mappings['bi'])
                expanded_keywords.add('data')
                expanded_keywords.add('analytics')
                expanded_keywords.add('analysis')

            # Special case for Excel
            if 'excel' in query.lower() or 'spreadsheet' in query.lower():
                expanded_keywords.update(skill_mappings['excel'])
                expanded_keywords.add('excel')
                expanded_keywords.add('microsoft excel')

            # Special case for PowerBI
            if 'power bi' in query.lower() or 'powerbi' in query.lower() or 'bi' in query.lower():
                expanded_keywords.update(skill_mappings['powerbi'])
                expanded_keywords.update(skill_mappings['bi'])
                expanded_keywords.add('power bi')
                expanded_keywords.add('powerbi')

            # Special case for Tableau
            if 'tableau' in query.lower() or 'visualization' in query.lower():
                expanded_keywords.update(skill_mappings['tableau'])
                expanded_keywords.update(skill_mappings['visualization'])
                expanded_keywords.add('tableau')
                expanded_keywords.add('data visualization')

            # Search in skills and experience
            q_objects = Q()
            for keyword in expanded_keywords:
                q_objects |= (
                    Q(skills__icontains=keyword) |
                    Q(experience__icontains=keyword) |
                    Q(projects__icontains=keyword)
                )
            students = students.filter(q_objects)

            # Log the search
            RecruiterSearch.objects.create(
                search_query=query,
                filters_used={
                    'skills': skills,
                    'location': location,
                    'experience_level': experience_level
                }
            )

            # Update analytics, excluding common words
            # Use original keywords for analytics to avoid over-counting expanded terms
            for keyword in keywords:
                # Skip common words and words shorter than 3 characters
                if keyword.lower() in COMMON_WORDS or len(keyword) < 3:
                    continue

                # Try to get the existing analytics object
                try:
                    analytics = Analytics.objects.get(skill_name=keyword)
                    # If it exists, update the search count
                    analytics.search_count = F('search_count') + 1
                    analytics.save()
                except Analytics.DoesNotExist:
                    # If it doesn't exist, create a new one with search_count=1
                    Analytics.objects.create(skill_name=keyword, search_count=1)

        if skills:
            skill_list = [s.strip() for s in skills.split(',') if s.strip()]
            if skill_list and nlp:
                # Create a Q object for OR filtering of skills
                skill_query = Q()
                expanded_skills = set()

                # Process each skill with NLP to get lemmas
                for skill in skill_list:
                    # Add the original skill
                    expanded_skills.add(skill)

                    # Process with spaCy to get lemmas
                    skill_doc = nlp(skill.lower())
                    for token in skill_doc:
                        if not token.is_stop and not token.is_punct:
                            expanded_skills.add(token.lemma_)

                            # Check if this lemma is in our skill mappings
                            if token.lemma_ in skill_mappings:
                                expanded_skills.update(skill_mappings[token.lemma_])

                            # Check if this lemma is in any of the values in skill mappings
                            for key, values in skill_mappings.items():
                                if token.lemma_ in values or token.text in values:
                                    expanded_skills.update([key] + values)

                # Build the query with expanded skills
                for skill in expanded_skills:
                    skill_query |= Q(skills__icontains=skill)

                students = students.filter(skill_query)

        if location:
            location_list = [loc.strip() for loc in location.split(',') if loc.strip()]
            if location_list:
                # Create a Q object for OR filtering of locations
                location_query = Q()
                for loc in location_list:
                    location_query |= Q(experience__icontains=loc)
                students = students.filter(location_query)

        if experience_level:
            students = students.filter(experience__icontains=experience_level)

    # Get popular searches from analytics (top 5 by search count), excluding common words
    popular_searches = Analytics.objects.exclude(skill_name__in=COMMON_WORDS).order_by('-search_count')[:5]

    # Get active skill filters from the database
    skill_filters = SkillFilter.objects.filter(is_active=True).order_by('order', 'name')

    # Apply sorting based on the sort option
    if form.is_valid():
        sort_option = form.cleaned_data.get('sort', 'relevance')
        if sort_option == 'recent':
            students = students.order_by('-created_at')
        elif sort_option == 'relevance':
            query = form.cleaned_data.get('query', '')
            # Check if expanded_keywords exists and has items
            if query and 'expanded_keywords' in locals() and expanded_keywords:
                # For relevance sorting with a query, calculate relevance scores
                # Create a dictionary to store relevance scores for each student
                relevance_scores = {}

                # Get all students as a list to manipulate
                student_list = list(students)

                # Calculate relevance score for each student
                for student in student_list:
                    score = 0

                    # Check skills field
                    if student.skills:
                        student_skills = student.skills.lower()
                        for keyword in expanded_keywords:
                            if keyword.lower() in student_skills:
                                score += 1
                                # Give extra points for exact matches
                                if any(skill.lower() == keyword.lower() for skill in student.get_skills_list()):
                                    score += 2

                    # Check experience field
                    if student.experience:
                        for keyword in expanded_keywords:
                            if keyword.lower() in student.experience.lower():
                                score += 1

                    # Check projects field
                    if student.projects:
                        for keyword in expanded_keywords:
                            if keyword.lower() in student.projects.lower():
                                score += 1

                    # Store the score
                    relevance_scores[student.id] = score

                # Sort students by relevance score (descending)
                student_list.sort(key=lambda x: (relevance_scores.get(x.id, 0), x.created_at), reverse=True)

                # Convert back to a queryset-like object
                students = student_list
            else:
                # If no query or expanded keywords, sort by most recently created
                students = students.order_by('-created_at')
    else:
        # Default sorting if form is not valid
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

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Please complete your profile.')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            # If the form is not valid, display a general error message
            if form.errors:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def profile(request):
    # Get or create the student profile for the current user
    student, _ = Student.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            # If the form is not valid, display a general error message
            if form.errors:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'core/profile.html', {'form': form, 'student': student})

@login_required
def delete_profile(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)
        user = request.user
        student.delete()
        user.delete()
        messages.success(request, 'Your profile has been deleted.')
        return redirect('home')
    return render(request, 'core/delete_profile.html')
