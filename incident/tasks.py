from core.celery import app
from django.core.exceptions import ValidationError
import datetime
from incident.models import EscalationLevelAssignment
from logger.models import Incident, Service
from logger.signals import escalation_builder


# TODO: figure out reason why the incident was created
# TODO: prepare events model
# TODO: incident builder can be shared across calls
@app.task
def create_incident(service_id):
    """
    Create a new incident and returns it's id
    """
    service = Service.objects.get(id=service_id)
    window = service.maintainance_policy

    current_time = datetime.datetime.now()
    incident = None
    # check if maintainance window is in effect
    if window.start_time > current_time or window.end_time < current_time:
        # deduplicate incidents associated with the given service
        if not (
            Incident.objects.filter(service=service, status="Acknowledged").exists()
            or Incident.objects.filter(service=service, status="Resolved").exists()
        ):
            incident = Incident.objects.get_or_create(
                service=service,
                status="Open",
            )[0]

    if incident is None:
        raise ValidationError("Couldn't create an incident for service")

    return incident.id


@app.task
def resolve_incident(service_id):
    """
    Resolves an existing incident
    """
    if Service.objects.filter(id=service_id).exists():
        # de-duplicate open incidents
        service = Service.objects.get(id=service_id)
        incident = Incident.objects.get(
            service=service,
            status="Open",
        )
        incident.status = "Resolved"
        incident.save()
