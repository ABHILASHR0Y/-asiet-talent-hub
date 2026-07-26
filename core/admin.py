from django.contrib import admin
from django.conf import settings
from .models import Student, RecruiterSearch, Analytics, SkillFilter

admin.site.site_header = settings.SITE_NAME
admin.site.site_title = settings.SITE_SHORT_NAME
admin.site.index_title = 'Platform Administration'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'skills')
    list_filter = ('created_at', 'updated_at')

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
