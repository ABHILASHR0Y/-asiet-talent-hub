from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student

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

class StudentProfileForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Python, JavaScript, React, etc.'}),
        help_text='Enter your skills separated by commas (e.g., Python, JavaScript, Machine Learning)',
        error_messages={'required': 'Please enter at least one skill'}
    )
    experience = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Describe your work experience here...'}),
        help_text='Describe your work experience',
        error_messages={'required': 'Please provide information about your experience'}
    )
    projects = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Describe your projects here...'}),
        required=False,
        help_text='Describe your projects (optional)'
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload a profile picture (optional)',
        error_messages={'invalid_image': 'The uploaded file is not a valid image'}
    )
    resume = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload your resume in PDF format (optional)',
        error_messages={'invalid': 'Please upload a valid file'}
    )

    class Meta:
        model = Student
        fields = ('skills', 'experience', 'projects', 'profile_picture', 'resume')

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            file_extension = resume.name.split('.')[-1].lower()
            if file_extension != 'pdf':
                raise forms.ValidationError('Please upload your resume in PDF format only.')
        return resume

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