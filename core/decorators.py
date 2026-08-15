from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def approved_recruiter_required(view_func):
    """Decorator ensuring the user is an approved recruiter."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to access the recruiter dashboard.")
            return redirect('login')

        if not hasattr(request.user, 'company_profile'):
            messages.error(request, "You need a recruiter account to access this page.")
            return redirect('recruiter_register')

        company = request.user.company_profile
        if company.verification_status != 'approved':
            return redirect('recruiter_pending')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def recruiter_required(view_func):
    """Decorator ensuring user has a recruiter company profile (even if pending)."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to access your recruiter account.")
            return redirect('login')

        if not hasattr(request.user, 'company_profile'):
            messages.error(request, "You need a recruiter account to access this page.")
            return redirect('recruiter_register')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    """Decorator ensuring user is a student (not a recruiter or placement admin)."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to access student features.")
            return redirect('login')

        if hasattr(request.user, 'company_profile'):
            messages.warning(request, "Recruiters should use the recruiter dashboard.")
            return redirect('recruiter_dashboard')

        if request.user.is_staff or request.user.is_superuser:
            messages.info(request, "Redirecting to Django Admin Panel.")
            return redirect('admin:index')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def placement_admin_required(view_func):
    """Decorator ensuring user is a Placement Cell Admin (staff/superuser)."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to access Django Admin.")
            return redirect('/admin/login/')

        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Access denied. Only Placement Cell Administrators can access Django Admin.")
            return redirect('home')

        return redirect('admin:index')
    return _wrapped_view

