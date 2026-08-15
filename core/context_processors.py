"""Template context processors for site-wide branding, user roles, and notifications."""
from django.conf import settings
from .models import CompanyProfile, Notification


def site_branding(request):
    """Expose ASIET Talent Hub branding constants, user role, and notification metrics to all templates."""
    user_role = 'guest'
    unread_notifications_count = 0
    pending_verifications_count = 0
    company_profile = None

    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

        if request.user.is_staff or request.user.is_superuser:
            user_role = 'admin'
            pending_verifications_count = CompanyProfile.objects.filter(verification_status='pending').count()
        elif hasattr(request.user, 'company_profile'):
            company_profile = request.user.company_profile
            if company_profile.verification_status == 'approved':
                user_role = 'approved_recruiter'
            else:
                user_role = 'pending_recruiter'
        else:
            user_role = 'student'

    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_SHORT_NAME': settings.SITE_SHORT_NAME,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'SITE_COLLEGE': settings.SITE_COLLEGE,
        'SITE_COLLEGE_SHORT': settings.SITE_COLLEGE_SHORT,
        'SITE_TAGLINE': settings.SITE_TAGLINE,
        'SITE_EMAIL': settings.DEFAULT_FROM_EMAIL,
        'user_role': user_role,
        'unread_notifications_count': unread_notifications_count,
        'pending_verifications_count': pending_verifications_count,
        'company_profile': company_profile,
    }

