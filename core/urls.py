from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public & Discovery
    path('', views.home, name='home'),
    path('discover/', views.discover, name='discover'),

    # Auth & Student Profile
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),

    # Recruiter Workflow
    path('recruiter/register/', views.recruiter_register, name='recruiter_register'),
    path('recruiter/pending/', views.recruiter_pending, name='recruiter_pending'),
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/profile/', views.recruiter_company_profile, name='recruiter_company_profile'),
    path('recruiter/jobs/create/', views.job_create, name='job_create'),
    path('recruiter/jobs/<int:job_id>/edit/', views.job_edit, name='job_edit'),
    path('recruiter/jobs/<int:job_id>/toggle/', views.job_toggle_status, name='job_toggle_status'),
    path('recruiter/jobs/<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('recruiter/jobs/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('recruiter/applications/<int:application_id>/status/', views.update_application_status, name='update_application_status'),

    # Student Job Ecosystem
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/applications/', views.student_applications, name='student_applications'),
    path('student/applications/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),

    # Jobs Portal
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.job_apply, name='job_apply'),
    path('jobs/<int:job_id>/save/', views.job_save_toggle, name='job_save_toggle'),

    # Placement Cell Admin (Redirects to Django Admin)
    path('placement-admin/', views.placement_admin_dashboard, name='placement_admin_dashboard'),

    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]