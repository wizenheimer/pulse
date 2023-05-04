from django.urls import path, include
from rest_framework.routers import DefaultRouter
from logger import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"endpoint", views.EndpointViewset, basename="logger_viewset")
router.register(r"cron", views.CronHandlerViewset, basename="cron_viewset")
router.register(r"request", views.RequestHandlerViewset, basename="request_viewset")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("team-subscribe/", views.teammate_subscribe, name="team-subscribe"),
    path("guest-subscribe/", views.guest_subscribe, name="guest-subscribe"),
    path("", include(router.urls)),
]
