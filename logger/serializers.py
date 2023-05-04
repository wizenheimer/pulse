from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Endpoint,
    CronHandler,
    RequestHandler,
)


class RequestHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestHandler
        fields = "__all__"


class EndpointSerializer(serializers.ModelSerializer):
    # NOTE: requests credentials are shared, has an independent endpoint
    request = RequestHandlerSerializer(read_only=True)

    class Meta:
        model = Endpoint
        fields = "__all__"
        extra_fields = ["request"]

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(EndpointSerializer, self).get_field_names(
            declared_fields, info
        )

        if getattr(self.Meta, "extra_fields", None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class CronHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronHandler
        fields = "__all__"
