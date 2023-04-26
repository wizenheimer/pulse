from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Monitor, MonitorResult
from users.models import MonitorAssignment
from .serializers import MonitorSerializer, MonitorResultSerializer


class MonitorViewset(viewsets.ModelViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        type = request.query_params.get("type", "Uptime Monitor Result")
        monitor = Monitor.objects.get(pk=pk)
        monitor_result = MonitorResult.objects.filter(
            type=type, monitor=monitor
        ).order_by("-checked_at")[:10]
        serializer = MonitorResultSerializer(monitor_result, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = serializer.data["user"]
        monitor = serializer.save()
        assignment = MonitorAssignment(user=user, monitor=monitor)
        assignment.save()
