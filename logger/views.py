from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import RequestHandler, Endpoint, CronHandler
from .serializers import (
    RequestHandlerSerializer,
    EndpointSerializer,
    CronHandlerSerializer,
)


class RequestHandlerViewset(viewsets.ModelViewSet):
    queryset = RequestHandler.objects.all()
    serializer_class = RequestHandlerSerializer


class EndpointViewset(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer


class CronHandlerViewset(viewsets.ModelViewSet):
    queryset = CronHandler.objects.all()
    serializer_class = CronHandlerSerializer
