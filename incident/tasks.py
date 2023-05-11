from core.celery import app
from logger.models import Incident, Service, Endpoint


# TODO: figure out reason why the incident was created
# TODO: prepare events model
@app.task
def create_incident(service_id):
    """
    Create a new incident
    """
    service = Service.objects.get(id=service_id)
    # TODO: create incident after the grace period
    # to deduplicate incidents associated with the given service
    incident = Incident.objects.get_or_create(
        service=service,
        status="Open",
    )


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
