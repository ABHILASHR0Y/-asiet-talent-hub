from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    course = models.CharField(max_length=100, blank=True, default='')
    department = models.CharField(max_length=100, blank=True, default='')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    skills = models.TextField(blank=True, default='')
    experience = models.TextField(blank=True, default='')
    projects = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def get_skills_list(self):
        """Return a list of skills, properly split and cleaned"""
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage based on filled fields"""
        total_points = 8
        score = 0
        if self.user.first_name and self.user.last_name:
            score += 1
        if self.course and self.department:
            score += 1
        if self.cgpa:
            score += 1
        if self.skills:
            score += 1
        if self.experience:
            score += 1
        if self.projects:
            score += 1
        if self.resume:
            score += 1
        if self.profile_picture:
            score += 1
        return int((score / total_points) * 100)


class CompanyProfile(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255)
    hr_name = models.CharField(max_length=255)
    official_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending'
    )
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_companies'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    def is_approved(self):
        return self.verification_status == 'approved'


class Job(models.Model):
    OPPORTUNITY_TYPE_CHOICES = [
        ('full_time', 'Full-Time'),
        ('internship', 'Internship'),
        ('part_time', 'Part-Time'),
    ]

    WORK_MODE_CHOICES = [
        ('on_site', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    ]

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=255)
    opportunity_type = models.CharField(max_length=50, choices=OPPORTUNITY_TYPE_CHOICES, default='full_time')
    description = models.TextField()
    location = models.CharField(max_length=255)
    work_mode = models.CharField(max_length=50, choices=WORK_MODE_CHOICES, default='on_site')
    required_skills = models.TextField(help_text="Comma-separated skills (e.g. Python, Django, MySQL)")
    preferred_skills = models.TextField(blank=True, default='', help_text="Comma-separated preferred skills")
    eligible_departments = models.TextField(
        blank=True, default='', help_text="Comma-separated eligible departments or empty for all"
    )
    minimum_cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    experience_required = models.CharField(max_length=100, blank=True, default='Freshers')
    salary_or_stipend = models.CharField(max_length=100, help_text="Salary or Internship stipend details")
    openings = models.IntegerField(default=1)
    deadline = models.DateTimeField()
    selection_process = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

    def is_expired(self):
        return timezone.now() > self.deadline

    def get_effective_status(self):
        if self.status == 'active' and self.is_expired():
            return 'expired'
        return self.status

    def is_accepting_applications(self):
        return self.company.is_approved() and self.status == 'active' and not self.is_expired()

    def get_required_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def get_preferred_skills_list(self):
        if not self.preferred_skills:
            return []
        return [s.strip() for s in self.preferred_skills.split(',') if s.strip()]

    def get_eligible_departments_list(self):
        if not self.eligible_departments:
            return []
        return [d.strip() for d in self.eligible_departments.split(',') if d.strip()]


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    cover_note = models.TextField(blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student} - {self.job.title}"


class SavedJob(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by_students')
    saved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-saved_at']
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student} saved {self.job.title}"


class JobView(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='job_views')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.student} viewed {self.job.title}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"


class RecruiterSearch(models.Model):
    search_query = models.TextField()
    filters_used = models.JSONField(default=dict)
    searched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.search_query[:50]}..."


class Analytics(models.Model):
    skill_name = models.CharField(max_length=255)
    search_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Analytics"

    def __str__(self):
        return f"{self.skill_name} ({self.search_count} searches)"


class SkillFilter(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the skill (e.g., Python, JavaScript)")
    display_name = models.CharField(max_length=100, help_text="How the skill should be displayed (e.g., Python, JavaScript)")
    is_active = models.BooleanField(default=True, help_text="Whether this skill filter is active and should be shown")
    order = models.PositiveIntegerField(default=0, help_text="Order in which the skill appears (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Skill Filter"
        verbose_name_plural = "Skill Filters"

    def __str__(self):
        return self.display_name

