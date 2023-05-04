from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Monitor, MonitorResult

# from users.models import MonitorAssignment
from .serializers import MonitorSerializer, MonitorResultSerializer, AlertSerializer

# from .permissions import isParent


class MonitorViewset(viewsets.ModelViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
