from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student, CompanyProfile, Job, JobApplication


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        error_messages={'required': 'Email is required', 'invalid': 'Please enter a valid email address'}
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
        error_messages={'required': 'First name is required'}
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
        error_messages={'required': 'Last name is required'}
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        error_messages={
            'required': 'Username is required',
            'unique': 'This username is already taken. Please choose another one.'
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'}),
        error_messages={'required': 'Password is required'}
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        error_messages={'required': 'Please confirm your password'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email or login.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match. Please try again.')
        return password2


class RecruiterRegistrationForm(forms.Form):
    company_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name (e.g. Acme Corp)'})
    )
    hr_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HR / Recruiter Full Name'})
    )
    official_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'official@company.com'}),
        help_text='Please use your official company email address.'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://company.com'})
    )
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country (e.g. Kochi, India)'})
    )
    industry = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry (e.g. Information Technology)'})
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Brief description of your company...'})
    )
    logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Company logo (optional)'
    )
    linkedin_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/company/profile'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'}),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        required=True
    )

    def clean_official_email(self):
        email = self.cleaned_data.get('official_email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered. Please use a different email or login.')
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match. Please try again.')
        return p2


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = (
            'company_name', 'hr_name', 'official_email', 'phone_number',
            'website', 'location', 'industry', 'description', 'logo', 'linkedin_url'
        )
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'official_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    course = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.Tech, MCA, M.Tech'}),
        help_text='Degree / Course'
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science, Electronics, Mechanical'}),
        help_text='Department / Major'
    )
    cgpa = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8.50', 'step': '0.01'}),
        help_text='Current CGPA (out of 10.0)'
    )
    graduation_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026'}),
        help_text='Year of Graduation'
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Short bio or career objective...'})
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Python, JavaScript, React, Django, SQL'}),
        help_text='Enter your skills separated by commas',
        required=False
    )
    experience = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Describe your work / internship experience...'}),
        required=False
    )
    projects = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Describe your academic or side projects...'}),
        required=False
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload a circular profile picture'
    )
    remove_profile_picture = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remove current profile picture'
    )
    resume = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload resume in PDF format'
    )

    class Meta:
        model = Student
        fields = (
            'course', 'department', 'cgpa', 'graduation_year', 'phone_number',
            'bio', 'skills', 'experience', 'projects', 'profile_picture', 'resume'
        )

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            file_extension = resume.name.split('.')[-1].lower()
            if file_extension != 'pdf':
                raise forms.ValidationError('Please upload your resume in PDF format only.')
        return resume


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = (
            'title', 'opportunity_type', 'work_mode', 'location',
            'description', 'required_skills', 'preferred_skills',
            'eligible_departments', 'minimum_cgpa', 'graduation_year',
            'experience_required', 'salary_or_stipend', 'openings',
            'deadline', 'selection_process', 'status'
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer Intern'}),
            'opportunity_type': forms.Select(attrs={'class': 'form-select'}),
            'work_mode': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kochi / Remote'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Detailed job description...'}),
            'required_skills': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Python, Django, SQL (comma-separated)'}),
            'preferred_skills': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Docker, AWS, React (optional)'}),
            'eligible_departments': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Computer Science, Electronics (or leave blank for all)'}),
            'minimum_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 7.0', 'step': '0.1'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026'}),
            'experience_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Freshers / 0-1 years'}),
            'salary_or_stipend': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₹25,000 / month or ₹6.5 LPA'}),
            'openings': forms.NumberInput(attrs={'class': 'form-control', 'value': 1}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'selection_process': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': '1. Aptitude Test -> 2. Technical Interview -> 3. HR Interview'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class JobApplicationForm(forms.ModelForm):
    cover_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Why are you a good fit for this role? (Optional)'})
    )
    custom_resume = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload a specific resume for this job (optional, defaults to profile resume)'
    )

    class Meta:
        model = JobApplication
        fields = ('cover_note',)


class JobFilterForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search jobs by title, skill, or keyword...'})
    )
    opportunity_type = forms.ChoiceField(
        choices=[('', 'All Types'), ('full_time', 'Full-Time'), ('internship', 'Internship'), ('part_time', 'Part-Time')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    work_mode = forms.ChoiceField(
        choices=[('', 'All Work Modes'), ('on_site', 'On-site'), ('remote', 'Remote'), ('hybrid', 'Hybrid')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by department'})
    )


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Search for talent (e.g., Python developer with ML experience)'
        })
    )
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by skills (comma-separated)',
            'id': 'skills-input'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by location',
            'id': 'location-input'
        })
    )
    experience_level = forms.ChoiceField(
        choices=[
            ('', 'Any Experience'),
            ('entry', 'Entry Level'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior Level')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'experience-level'})
    )
    sort = forms.ChoiceField(
        choices=[
            ('relevance', 'Relevant'),
            ('recent', 'Recent'),
        ],
        required=False,
        initial='relevance',
        widget=forms.HiddenInput(attrs={'id': 'sort-input'})
    )