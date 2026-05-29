from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Project, User, ProjectMember, Camera,
    SafetyViolation, InjuryAlert, InactivityAlert,
    DailyProgressUpdate, Report
)

# ─────────────────────────────────────────
# Admin Site Branding
# ─────────────────────────────────────────
admin.site.site_header = "ConstructEYE Administration"
admin.site.site_title = "ConstructEYE Admin"
admin.site.index_title = "ConstructEYE Operations Dashboard"


# ─────────────────────────────────────────
# Inline Configurations
# ─────────────────────────────────────────

class ProjectMemberInline(admin.TabularInline):
    """
    Shows all members of a project directly
    when viewing/editing a project record.
    extra=0 means no empty extra rows shown.
    """
    model = ProjectMember
    extra = 0


class CameraInline(admin.TabularInline):
    """
    Shows all cameras belonging to a project
    when viewing/editing a project record.
    camera_id is readonly — auto generated.
    """
    model = Camera
    extra = 0
    readonly_fields = ('camera_id',)


class SafetyViolationInline(admin.TabularInline):
    """
    Shows all safety violations detected by a camera
    when viewing/editing a camera record.
    """
    model = SafetyViolation
    extra = 0
    readonly_fields = ('violation_id', 'created_at', 'evidence_storage_key')


class InjuryAlertInline(admin.TabularInline):
    """
    Shows all injury alerts detected by a camera
    when viewing/editing a camera record.
    """
    model = InjuryAlert
    extra = 0
    readonly_fields = ('alert_id', 'created_at', 'evidence_storage_key')


class InactivityAlertInline(admin.TabularInline):
    """
    Shows all inactivity alerts detected by a camera
    when viewing/editing a camera record.
    """
    model = InactivityAlert
    extra = 0
    readonly_fields = ('alert_id', 'created_at')


# ─────────────────────────────────────────
# Core Model Admins
# ─────────────────────────────────────────

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Project list shows key info at a glance.
    project_id and project_code are readonly —
    project_id is auto-generated UUID,
    project_code should never change after creation.
    Inlines show members and cameras directly inside the project.
    """
    list_display = ('project_name', 'project_code', 'location_address', 'start_date')
    search_fields = ('project_name', 'project_code', 'location_address')
    list_filter = ('start_date',)
    readonly_fields = ('project_id', 'project_code')
    inlines = [ProjectMemberInline, CameraInline]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extends Django's built-in UserAdmin to include
    our custom 'role' field.
    Filters by role and active status for quick management.
    """
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')

    # Add 'role' to the default fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """
    Shows which user belongs to which project.
    user__role lets us see the member's role directly in the list.
    autocomplete_fields requires search_fields on User and Project admins.
    """
    list_display = ('user', 'project', 'user__role')
    list_filter = ('project',)
    search_fields = ('user__username', 'project__project_name')
    autocomplete_fields = ('user', 'project')

    def user__role(self, obj):
        return obj.user.role
    user__role.short_description = 'Role'


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    """
    Camera list shows which project each camera belongs to.
    Inlines show all violations and alerts detected by each camera.
    camera_id is readonly — auto-generated UUID.
    """
    list_display = ('camera_id', 'project', 'location_description', 'stream_url')
    list_filter = ('project',)
    search_fields = ('location_description', 'project__project_name')
    readonly_fields = ('camera_id',)
    inlines = [SafetyViolationInline, InjuryAlertInline, InactivityAlertInline]


@admin.register(DailyProgressUpdate)
class DailyProgressUpdateAdmin(admin.ModelAdmin):
    """
    Progress updates ordered by newest first.
    update_id and created_at are readonly.
    Filtered by project and date for quick monitoring.
    """
    list_display = ('project', 'progress_percentage', 'created_at')
    list_filter = ('project', 'created_at')
    readonly_fields = ('update_id', 'created_at')
    ordering = ('-created_at',)


@admin.register(SafetyViolation)
class SafetyViolationAdmin(admin.ModelAdmin):
    """
    Safety violations list with filters by project, type and date.
    violation_id and created_at are readonly — auto-generated.
    """
    list_display = ('violation_type', 'project', 'camera', 'created_at')
    list_filter = ('project', 'violation_type', 'created_at')
    search_fields = ('violation_type', 'project__project_name')
    readonly_fields = ('violation_id', 'created_at')
    ordering = ('-created_at',)


@admin.register(InjuryAlert)
class InjuryAlertAdmin(admin.ModelAdmin):
    """
    Injury alerts list with filters by project, type and date.
    """
    list_display = ('alert_type', 'project', 'camera', 'created_at')
    list_filter = ('project', 'alert_type', 'created_at')
    search_fields = ('alert_type', 'project__project_name')
    readonly_fields = ('alert_id', 'created_at')
    ordering = ('-created_at',)


@admin.register(InactivityAlert)
class InactivityAlertAdmin(admin.ModelAdmin):
    """
    Inactivity alerts list with filters by project and date.
    """
    list_display = ('project', 'camera', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('project__project_name',)
    readonly_fields = ('alert_id', 'created_at')
    ordering = ('-created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Reports list showing type, project and creation date.
    report_id and created_at are readonly.
    """
    list_display = ('report_type', 'project', 'created_at')
    list_filter = ('project', 'report_type', 'created_at')
    search_fields = ('report_type', 'project__project_name')
    readonly_fields = ('report_id', 'created_at')
    ordering = ('-created_at',)