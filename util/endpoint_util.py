from django.contrib.contenttypes.models import ContentType
from logger.models import Endpoint, Service, Log
from .logger_util import process_endpoint


def prepare_logs_laggard():
    # NOTE: Not optimized, however signals would be triggered for each log instance
    # get all active services
    # print("# get all active services")
    services = Service.objects.filter(is_active=True)
    for service in services:
        # get all endpoints
        # print("# get all endpoints")
        endpoints = service.endpoints.all()
        for endpoint in endpoints:
            result = process_endpoint(endpoint)
            log = Log.objects.create(
                response_time=result.get("response_time", 0),
                status=result.get("status", "DOWN"),
                message=result.get("message"),
                entity_type=ContentType.objects.get_for_model(Endpoint),
                entity_id=endpoint.pk,
            )
            response_body = result.get("response_body", None)
            if response_body is not None:
                log.response_body = response_body
            # utilize signals for creating incidents
            # print("# utilize signals for creating incidents")
            log.save()


def prepare_logs_optimized():
    services = Service.objects.filter(is_active=True)

    # Instead of creating each Log instance individually in a loop, can use the bulk_create() method to create multiple instances in a single database query
    log_instances = []
    for service in services:
        for endpoint in service.endpoints.all():
            result = process_endpoint(endpoint)
            log = Log(
                response_time=result.get("response_time", 0),
                status=result.get("status", "DOWN"),
                message=result.get("message"),
                entity_type=ContentType.objects.get_for_model(Endpoint),
                entity_id=endpoint.pk,
            )
            response_body = result.get("response_body", None)
            if response_body is not None:
                log.response_body = response_body
            log_instances.append(log)
    Log.objects.bulk_create(log_instances)
