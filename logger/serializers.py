import json
from itertools import chain, combinations
from numpy import empty
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Endpoint, CronHandler, RequestHandler, Collection


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


# TODO: exclude is_active para
# TODO: build region validator
# TODO: clean up validation junk
# TODO: Snignal queue configuration
# TODO: Celery configuration with Redis
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

        timeout = attrs.get("timeout")
        check_frequency = attrs.get("check_frequency")

        if check_frequency < timeout:
            return ValidationError(
                "Frequency must never be set to a shorter amount of time than the Request timeout period"
            )

        regions = attrs.get("regions")
        region_list = set(list(regions.split("-")))
        allowed_regions = set(["us", "eu", "as", "au"])
        diff = region_list.difference(allowed_regions)
        if len(diff) != 0:
            ValidationError("No subset of regions is present in my_list")

        return super().validate(attrs)


class CronHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CronHandler
        fields = "__all__"


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"
