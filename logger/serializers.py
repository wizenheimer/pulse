from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .models import (
    Endpoint,
    CronHandler,
    Incident,
    Log,
    MaintainancePolicy,
    RequestHandler,
    Service,
)
from logger.documents import LogDocument


# TODO: Snignal queue configuration
class RequestHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestHandler
        fields = "__all__"


class EndpointSerializer(serializers.ModelSerializer):
    # NOTE: requests credentials are shared, has an independent endpoint
    request = RequestHandlerSerializer(read_only=True, required=False)

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

    def validate(self, attrs):
        port = attrs.get("port", None)
        type = attrs.get("type", None)

        # PORT VALIDATION : Required if monitor_type is set to tcp, udp, smtp, pop, or imap.
        if port is None and type in ["tcp", "udp", "smtp", "pop", "imap"]:
            return ValidationError(
                "Port required if monitor_type is set to tcp, udp, smtp, pop, or imap."
            )
        elif port is not None and type in ["smtp", "pop", "imap"]:
            if type == "smtp" and port not in [25, 465, 587]:
                return ValidationError("Invalid port")
            elif type == "pop" and port not in [110, 995]:
                return ValidationError("Invalid port")
            elif type == "imap" and port not in [110, 143]:
                return ValidationError("Invalid port")

        timeout = attrs.get("timeout", None)
        check_frequency = attrs.get("check_frequency", None)

        if timeout is None or check_frequency is None:
            return ValidationError("Timeout or Frequency missing.")

        if check_frequency <= timeout:
            return ValidationError(
                "Frequency must never be set to a shorter amount of time than the Request timeout period."
            )

        return super().validate(attrs)


class CronHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronHandler
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class LogDocumentSerializer(DocumentSerializer):
    class Meta:
        document = LogDocument
        fields = (
            "status",
            "response_time",
            "response_body",
            "message",
            "target",
        )


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = "__all__"


class MaintainanceWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintainancePolicy
        fields = "__all__"
