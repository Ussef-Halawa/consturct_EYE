from django.contrib import admin
from .models import Project, User, ProjectMember, Camera, SafetyViolation, InjuryAlert, InactivityAlert, DailyProgressUpdate, Report

admin.site.register(Project)
admin.site.register(User)
admin.site.register(ProjectMember)
admin.site.register(Camera)
admin.site.register(SafetyViolation)
admin.site.register(InjuryAlert)
admin.site.register(InactivityAlert)
admin.site.register(DailyProgressUpdate)
admin.site.register(Report)