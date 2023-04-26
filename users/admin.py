from django.contrib import admin
from monitor.models import Monitor, MonitorResult
from .models import (
    User,
    Team,
    TeamAssignment,
    Subscriber,
    SubscriberAssignment,
    MonitorAssignment,
)


# Register the Monitor model
class MonitorAdmin(admin.ModelAdmin):
    list_display = ("id", "url", "port", "timeout", "last_checked", "is_active")
    search_fields = ("url",)


admin.site.register(Monitor, MonitorAdmin)


# Register the MonitorResult model
class MonitorResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "monitor",
        "response_time",
        "status_code",
        "checked_at",
        "type",
    )
    search_fields = ("monitor__url",)


admin.site.register(MonitorResult, MonitorResultAdmin)

# Register the User model
admin.site.register(User)


# Register the Team model
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "token")
    search_fields = ("title", "description")


admin.site.register(Team, TeamAdmin)


# Register the TeamAssignment model
class TeamAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "team",
        "can_add_teammate",
        "can_remove_teammate",
        "begin_date",
    )
    search_fields = ("user__email", "team__title")


admin.site.register(TeamAssignment, TeamAssignmentAdmin)


# Register the Subscriber model
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("id", "email")
    search_fields = ("email",)


admin.site.register(Subscriber, SubscriberAdmin)


# Register the SubscriberAssignment model
class SubscriberAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subscriber",
        "monitor",
        "fetch_uptime",
        "fetch_port",
        "fetch_ssl",
        "fetch_speed",
    )
    search_fields = ("subscriber__email", "monitor__url")


admin.site.register(SubscriberAssignment, SubscriberAssignmentAdmin)


# Register the MonitorAssignment model
class MonitorAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "monitor", "is_admin", "begin_date")
    search_fields = ("user__email", "monitor__url")


admin.site.register(MonitorAssignment, MonitorAssignmentAdmin)
