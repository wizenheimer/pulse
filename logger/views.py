import re
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .pagination import StandardResultsSetPagination, LargeResultsSetPagination
from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import (
    SearchFilterBackend,
    FilteringFilterBackend,
    SuggesterFilterBackend,
)
from .models import (
    MaintainancePolicy,
    RequestHandler,
    Endpoint,
    CronHandler,
    SubscriberAssignment,
    GuestAssignment,
    Service,
    Incident,
    Log,
)
from users.models import User, Guest
from .serializers import (
    IncidentSerializer,
    MaintainanceWindowSerializer,
    RequestHandlerSerializer,
    EndpointSerializer,
    CronHandlerSerializer,
    ServiceSerializer,
    IncidentSerializer,
    LogDocumentSerializer,
)
from .documents import LogDocument


class RequestHandlerViewset(viewsets.ModelViewSet):
    queryset = RequestHandler.objects.all()
    serializer_class = RequestHandlerSerializer


class ServiceViewset(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    @action(detail=True, methods=["get"])
    def fetch(self, request, pk=None):
        service = get_object_or_404(Service, pk=pk)
        endpoints = service.endpoints.all().values_list("id", flat=True)
        crons = service.crons.all().values_list("id", flat=True)
        return Response(
            {
                "endpoints": endpoints,
                "crons": crons,
            },
            status=200,
        )

    @action(detail=True, methods=["get"])
    def subscribers(self, request, pk=None):
        service = get_object_or_404(Service, pk=pk)
        subscribers = service.subscribers.all().values_list("email", flat=True)
        if not service.is_public:
            return Response(
                {"subscribers": "subscribers empty since service is not public"}
            )
        if not service.is_active:
            return Response(
                {"subscribers": "subscribers empty since service is not active"}
            )
        return Response({"subscibers": subscribers}, status=200)

    @action(detail=True, methods=["get"])
    def guests(self, request, pk=None):
        service = get_object_or_404(Service, pk=pk)
        if not service.is_public:
            return Response({"guests": "guests empty since endpoint is not public"})
        if not service.is_active:
            return Response({"guests": "guests empty since endpoint is not active"})
        guests = service.guests.all().values_list("email", flat=True)
        return Response({"subscibers": guests}, status=200)


class EndpointViewset(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer


class CronHandlerViewset(viewsets.ModelViewSet):
    queryset = CronHandler.objects.all()
    serializer_class = CronHandlerSerializer


class IncidentViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer

    @action(detail=True, methods=["post"])
    def status(self, request, pk=None):
        status = request.data.get("status", None)
        if status is None or status not in [
            "Open",
            "Acknowledged",
            "Resolved",
        ]:
            raise ValidationError("Invalid status")

        incident = get_object_or_404(Incident, pk=pk)
        incident.status = status
        incident.save()
        return Response(
            {
                "status": incident.status,
            },
            status=200,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def teammate_subscribe(request, pk=None):
    user = request.user
    intent = request.data.get("intent", None)

    # intent validators
    if intent not in ["add", "remove"]:
        return Response(
            {"error": "Intent is required for handling subscription."},
            status=400,
        )
    service = get_object_or_404(Service, pk=pk)

    # team validation - cross team access is denied
    if not service.team in User.teams.all() and not service.is_public:
        return Response({"error": "You aren't authorized to access this endpoint."})

    # subscription handlers
    if intent == "add":
        if service.subscribers.filter(id=user.id).exists():
            return Response({"error": "You already have a subscription."})
        assignment = SubscriberAssignment(user=user, service=service)
        assignment.save()
        message = "Successfully subscribed."
    else:
        if not service.subscribers.filter(id=user.id).exists():
            return Response({"error": "You are not subscribed."})
        service.subscribers.remove(user)
        service.save()
        message = "Successfully unsubscribed."

    return Response({"success": message}, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def guest_subscribe(request, pk=None):
    email = request.data.get("email")
    guest = Guest.get_or_create(email=email)
    intent = request.data.get("intent", None)

    # intent validators
    if intent not in ["add", "remove"]:
        return Response(
            {"error": "Intent is required for handling subscription."},
            status=400,
        )

    service = get_object_or_404(Service, pk=pk)

    # team validation - cross team access is denied
    if not service.is_public:
        return Response({"error": "You aren't authorized to access this endpoint."})

    # subscription handler
    if intent == "add":
        if service.guests.filter(id=guest.id).exists():
            return Response({"error": "You already have a subscription."})
        assignment = GuestAssignment(guest=guest, service=service)
        assignment.save()
        message = "Successfully subscribed."
    else:
        if not service.guests.filter(id=guest.id).exists():
            return Response({"error": "You are not subscribed."})
        service.guests.remove(guest)
        service.save()
        message = "Successfully unsubscribed."

    return Response({"success": message}, status=201)


class LogViewset(DocumentViewSet):
    document = LogDocument
    serializer_class = LogDocumentSerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [
        SearchFilterBackend,
        FilteringFilterBackend,
        SuggesterFilterBackend,
    ]

    search_fields = (
        "status",
        "response_time",
        "message",
        "response_body",
        "target",
    )

    filter_fields = {"status": "status"}


class MaintainanceWindowViewset(viewsets.ModelViewSet):
    queryset = MaintainancePolicy.objects.all()
    serializer = MaintainanceWindowSerializer
