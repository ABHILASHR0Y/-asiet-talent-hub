"""Template context processors for site-wide branding and metadata."""


def site_branding(request):
    """Expose ASIET Talent Hub branding constants to all templates."""
    from django.conf import settings

    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_SHORT_NAME': settings.SITE_SHORT_NAME,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'SITE_COLLEGE': settings.SITE_COLLEGE,
        'SITE_COLLEGE_SHORT': settings.SITE_COLLEGE_SHORT,
        'SITE_TAGLINE': settings.SITE_TAGLINE,
        'SITE_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }
