from django.urls import path, include
from rest_framework.routers import DefaultRouter
from incident import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"calendar", views.OnCallCalendarViewset, basename="calendar_viewset")
router.register(
    r"policy",
    views.EscalationPolicyViewset,
    basename="policy_viewset",
)
router.register(
    r"level",
    views.EscalationLevelViewset,
    basename="level_viewset",
)
router.register(
    r"action",
    views.EscaltionActionViewset,
    basename="action_viewset",
)
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
