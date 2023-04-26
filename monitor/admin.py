from django.contrib import admin

# from .models import Monitor, MonitorResult

# admin.site.register(Monitor)
# admin.site.register(MonitorResult)


# class MonitorResultInline(admin.TabularInline):
#     model = MonitorResult
#     extra = 0


# @admin.register(Monitor)
# class MonitorAdmin(admin.ModelAdmin):
#     inlines = [MonitorResultInline]
#     list_display = (
#         "url",
#         "port",
#         "timeout",
#         "last_checked",
#         "is_active",
#         "test_uptime",
#         "test_port",
#         "test_ssl",
#         "test_speed",
#     )
#     list_filter = ("is_active", "test_uptime", "test_port", "test_ssl", "test_speed")
#     search_fields = ("url",)


# @admin.register(MonitorResult)
# class MonitorResultAdmin(admin.ModelAdmin):
#     list_display = ("monitor", "response_time", "status_code", "type", "checked_at")
#     list_filter = ("type",)
#     search_fields = ("monitor__url",)
