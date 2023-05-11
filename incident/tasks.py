from core.celery import app
import datetime
from logger.models import Incident, Service


# TODO: figure out reason why the incident was created
# TODO: prepare events model
@app.task
def create_incident(service_id):
    """
    Create a new incident
    """
    service = Service.objects.get(id=service_id)
    window = service.maintainance_policy

    current_time = datetime.datetime.now()
    # check if maintainance window is in effect
    if window.start_time > current_time or window.end_time < current_time:
        # deduplicate incidents associated with the given service
        incident = Incident.objects.get_or_create(
            service=service,
            status="Open",
        )
    # TODO: create incident after the grace period


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
