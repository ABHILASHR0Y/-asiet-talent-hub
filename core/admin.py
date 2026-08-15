from django.contrib import admin
from django.conf import settings
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q
from .models import (
    Student, CompanyProfile, Job, JobApplication, SavedJob,
    JobView, Notification, RecruiterSearch, Analytics, SkillFilter
)
from .recommendations import calculate_job_match

admin.site.site_header = f"{settings.SITE_NAME} Admin"
admin.site.site_title = f"{settings.SITE_SHORT_NAME} Portal"
admin.site.index_title = "Placement Cell Central Control Center"


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'company_name', 'hr_name', 'official_email', 'phone_number',
        'industry', 'verification_status_badge', 'created_at'
    )
    list_filter = ('verification_status', 'industry', 'created_at')
    search_fields = ('company_name', 'hr_name', 'official_email', 'location', 'industry')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = ['approve_recruiters', 'reject_recruiters', 'suspend_recruiters']

    readonly_fields = (
        'verified_by', 'verified_at', 'total_jobs_posted',
        'active_jobs_count', 'closed_jobs_count', 'total_applications_count',
        'shortlisted_candidates_count'
    )

    fieldsets = (
        ('Company Information', {
            'fields': (
                'company_name', 'logo', 'industry', 'description',
                'website', 'linkedin_url', 'location'
            )
        }),
        ('Recruiter Contact', {
            'fields': ('hr_name', 'official_email', 'phone_number', 'user')
        }),
        ('Verification Status', {
            'fields': (
                'verification_status', 'verified_by', 'verified_at', 'rejection_reason'
            )
        }),
        ('Recruitment Activity Summary', {
            'fields': (
                'total_jobs_posted', 'active_jobs_count', 'closed_jobs_count',
                'total_applications_count', 'shortlisted_candidates_count'
            )
        }),
    )

    def verification_status_badge(self, obj):
        if obj.verification_status == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">✓ Verified by ASIET</span>')
        elif obj.verification_status == 'pending':
            return format_html('<span style="color: #d97706; font-weight: bold;">⏳ Pending Verification</span>')
        elif obj.verification_status == 'rejected':
            return format_html('<span style="color: red; font-weight: bold;">✕ Rejected</span>')
        elif obj.verification_status == 'suspended':
            return format_html('<span style="color: darkred; font-weight: bold;">🚫 Suspended</span>')
        return obj.get_verification_status_display()
    verification_status_badge.short_description = "Status"

    def approve_recruiters(self, request, queryset):
        count = 0
        for company in queryset:
            company.verification_status = 'approved'
            company.verified_by = request.user
            company.verified_at = timezone.now()
            company.rejection_reason = ''
            company.save()

            Notification.objects.create(
                recipient=company.user,
                notification_type='verification_approved',
                title='Company Account Approved!',
                message=f'Congratulations! Your company account for {company.company_name} has been verified by the ASIET Placement Cell.'
            )
            count += 1
        self.message_user(request, f"{count} company account(s) approved successfully.")
    approve_recruiters.short_description = "Approve Selected Recruiters"

    def reject_recruiters(self, request, queryset):
        count = queryset.update(verification_status='rejected')
        self.message_user(request, f"{count} company account(s) rejected.")
    reject_recruiters.short_description = "Reject Selected Recruiters"

    def suspend_recruiters(self, request, queryset):
        count = queryset.update(verification_status='suspended')
        self.message_user(request, f"{count} company account(s) suspended.")
    suspend_recruiters.short_description = "Suspend Selected Recruiters"

    def total_jobs_posted(self, obj):
        return obj.jobs.count()
    total_jobs_posted.short_description = "Total Jobs Posted"

    def active_jobs_count(self, obj):
        return obj.jobs.filter(status='active', deadline__gt=timezone.now()).count()
    active_jobs_count.short_description = "Active Jobs"

    def closed_jobs_count(self, obj):
        return obj.jobs.filter(Q(status='closed') | Q(deadline__lte=timezone.now())).count()
    closed_jobs_count.short_description = "Closed / Expired Jobs"

    def total_applications_count(self, obj):
        return JobApplication.objects.filter(job__company=obj).count()
    total_applications_count.short_description = "Total Applications Received"

    def shortlisted_candidates_count(self, obj):
        return JobApplication.objects.filter(job__company=obj, status__in=['shortlisted', 'selected', 'interview_scheduled']).count()
    shortlisted_candidates_count.short_description = "Shortlisted Candidates"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company_link', 'opportunity_type', 'work_mode',
        'status_badge', 'applications_count', 'deadline', 'created_at'
    )
    list_filter = ('status', 'opportunity_type', 'work_mode', 'created_at')
    search_fields = ('title', 'company__company_name', 'required_skills', 'location')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ['company', 'posted_by']
    list_select_related = ['company', 'posted_by']
    actions = ['close_selected_jobs', 'deactivate_selected_jobs', 'activate_selected_jobs']

    fieldsets = (
        ('Job Overview', {
            'fields': ('title', 'company', 'posted_by', 'opportunity_type', 'work_mode', 'location', 'description')
        }),
        ('Requirements & Eligibility', {
            'fields': ('required_skills', 'preferred_skills', 'eligible_departments', 'minimum_cgpa', 'graduation_year', 'experience_required')
        }),
        ('Compensation & Process', {
            'fields': ('salary_or_stipend', 'openings', 'deadline', 'selection_process')
        }),
        ('Status Configuration', {
            'fields': ('status',)
        }),
    )

    def company_link(self, obj):
        if obj.company.is_approved():
            return format_html('<strong>{}</strong> <span style="color:green;">✓</span>', obj.company.company_name)
        return obj.company.company_name
    company_link.short_description = "Company"

    def status_badge(self, obj):
        if obj.status == 'active' and not obj.is_expired():
            return format_html('<span style="color: green; font-weight: bold;">Active</span>')
        elif obj.is_expired():
            return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
        return obj.get_status_display()
    status_badge.short_description = "Status"

    def applications_count(self, obj):
        return obj.applications.count()
    applications_count.short_description = "Applications"

    def close_selected_jobs(self, request, queryset):
        count = queryset.update(status='closed')
        self.message_user(request, f"{count} job posting(s) closed.")
    close_selected_jobs.short_description = "Close Selected Jobs"

    def deactivate_selected_jobs(self, request, queryset):
        count = queryset.update(status='closed')
        self.message_user(request, f"{count} job posting(s) deactivated by admin.")
    deactivate_selected_jobs.short_description = "Deactivate Selected Jobs"

    def activate_selected_jobs(self, request, queryset):
        count = queryset.update(status='active')
        self.message_user(request, f"{count} job posting(s) activated.")
    activate_selected_jobs.short_description = "Activate Selected Jobs"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'job_title', 'company_name', 'applied_at',
        'status_badge', 'ai_match_score_display'
    )
    list_filter = ('status', 'applied_at')
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'student__user__username', 'student__user__email',
        'job__title', 'job__company__company_name'
    )
    ordering = ('-applied_at',)
    date_hierarchy = 'applied_at'
    autocomplete_fields = ['student', 'job']
    list_select_related = ['student__user', 'job__company']

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = "Job"

    def company_name(self, obj):
        return obj.job.company.company_name
    company_name.short_description = "Company"

    def status_badge(self, obj):
        colors = {
            'applied': 'blue',
            'under_review': 'purple',
            'shortlisted': 'green',
            'interview_scheduled': 'orange',
            'selected': 'teal',
            'rejected': 'red',
            'withdrawn': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = "Status"

    def ai_match_score_display(self, obj):
        match_info = calculate_job_match(obj.student, obj.job)
        score = match_info['match_score']
        return format_html('<span style="font-family: monospace; font-weight: bold; background: #FEF08A; padding: 2px 8px; border-radius: 12px;">{}% Match</span>', score)
    ai_match_score_display.short_description = "AI Match Score"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_name', 'course', 'department', 'cgpa',
        'graduation_year', 'phone_number', 'profile_completion', 'created_at'
    )
    list_filter = ('department', 'course', 'graduation_year', 'created_at')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'user__email', 'skills', 'department', 'course'
    )
    ordering = ('-created_at',)
    autocomplete_fields = ['user']
    list_select_related = ['user']

    def student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    student_name.short_description = "Student Name"

    def profile_completion(self, obj):
        pct = obj.get_profile_completion_percentage()
        color = "green" if pct == 100 else ("orange" if pct >= 50 else "red")
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, pct)
    profile_completion.short_description = "Completion"


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'saved_at')
    list_select_related = ['student__user', 'job']


@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'viewed_at')
    list_select_related = ['student__user', 'job']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')


@admin.register(RecruiterSearch)
class RecruiterSearchAdmin(admin.ModelAdmin):
    list_display = ('search_query', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('search_query',)


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'search_count')
    list_filter = ('search_count',)
    search_fields = ('skill_name',)


@admin.register(SkillFilter)
class SkillFilterAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'is_active', 'order')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'display_name')
    list_editable = ('is_active', 'order')
    ordering = ('order', 'name')
