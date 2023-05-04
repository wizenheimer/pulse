import re
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    RequestHandler,
    Endpoint,
    CronHandler,
    SubscriberAssignment,
    GuestAssignment,
    Collection,
    CronSubscriberAssignment,
)
from users.models import User, Guest
from .serializers import (
    RequestHandlerSerializer,
    EndpointSerializer,
    CronHandlerSerializer,
    CollectionSerializer,
)


class RequestHandlerViewset(viewsets.ModelViewSet):
    queryset = RequestHandler.objects.all()
    serializer_class = RequestHandlerSerializer


class CollectionViewset(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    @action(detail=True, methods=["get"])
    def fetch(self, request, pk=None):
        collection = get_object_or_404(Collection, pk=pk)
        endpoints = collection.endpoints.all().values_list("id", flat=True)
        crons = collection.crons.all().values_list("id", flat=True)
        return Response(
            {
                "endpoints": endpoints,
                "crons": crons,
            },
            status=200,
        )


class EndpointViewset(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer

    @action(detail=True, methods=["get"])
    def subscribers(self, request, pk=None):
        endpoint = get_object_or_404(Endpoint, pk=pk)
        subscribers = endpoint.subscribers.all().values_list("email", flat=True)
        if not endpoint.is_public:
            return Response(
                {"subscribers": "subscribers empty since endpoint is not public"}
            )
        if not endpoint.is_active:
            return Response(
                {"subscribers": "subscribers empty since endpoint is not active"}
            )
        return Response({"subscibers": subscribers}, status=200)

    @action(detail=True, methods=["get"])
    def guests(self, request, pk=None):
        endpoint = get_object_or_404(Endpoint, pk=pk)
        if not endpoint.is_public:
            return Response({"guests": "guests empty since endpoint is not public"})
        if not endpoint.is_active:
            return Response({"guests": "guests empty since endpoint is not active"})
        guests = endpoint.guests.all().values_list("email", flat=True)
        return Response({"subscibers": guests}, status=200)


class CronHandlerViewset(viewsets.ModelViewSet):
    queryset = CronHandler.objects.all()
    serializer_class = CronHandlerSerializer


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
    endpoint = get_object_or_404(Endpoint, pk=pk)

    # team validation - cross team access is denied
    if not endpoint.team in User.teams.all() and not endpoint.is_public:
        return Response({"error": "You aren't authorized to access this endpoint."})

    # subscription handlers
    if intent == "add":
        if endpoint.subscribers.filter(id=user.id).exists():
            return Response({"error": "You already have a subscription."})
        assignment = SubscriberAssignment(user=user, endpoint=endpoint)
        assignment.save()
        message = "Successfully subscribed."
    else:
        if not endpoint.subscribers.filter(id=user.id).exists():
            return Response({"error": "You are not subscribed."})
        endpoint.subscribers.remove(user)
        endpoint.save()
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

    endpoint = get_object_or_404(Endpoint, pk=pk)

    # team validation - cross team access is denied
    if not endpoint.is_public:
        return Response({"error": "You aren't authorized to access this endpoint."})

    # subscription handler
    if intent == "add":
        if endpoint.guests.filter(id=guest.id).exists():
            return Response({"error": "You already have a subscription."})
        assignment = GuestAssignment(guest=guest, endpoint=endpoint)
        assignment.save()
        message = "Successfully subscribed."
    else:
        if not endpoint.guests.filter(id=guest.id).exists():
            return Response({"error": "You are not subscribed."})
        endpoint.guests.remove(guest)
        endpoint.save()
        message = "Successfully unsubscribed."

    return Response({"success": message}, status=201)
