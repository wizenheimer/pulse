from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Monitor, MonitorResult

# from users.models import MonitorAssignment
from .serializers import MonitorSerializer, MonitorResultSerializer
from .permissions import isParent


class MonitorViewset(viewsets.ModelViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    permission_classes = [isParent]

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        monitor = Monitor.objects.get(pk=pk)
        if not monitor.users.filter(id=request.user.id).exists():
            return Response({"error": "You are not authorized to perform this action."})
        type = request.query_params.get("type", "Uptime Monitor Result")
        monitor_result = MonitorResult.objects.filter(
            type=type, monitor=monitor
        ).order_by("checked_at")
        serializer = MonitorResultSerializer(monitor_result, many=True)
        return Response(serializer.data)

    # def perform_create(self, serializer):
    #     # user = serializer.validated_data["user"]
    #     user = self.request.user
    #     monitor = serializer.save()
    #     assignment = MonitorAssignment(user=user, monitor=monitor)
    #     assignment.save()
