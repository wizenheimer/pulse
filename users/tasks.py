from core.celery import app
from .models import User, Team, TeamAssignment
from logger.tasks import (
    send_email_notification,
    send_text_notification,
    send_webhook_notification,
)


@app.task
def notify_user(user_id, team_id, incident_id, priority="Low"):
    """
    Figure out the notification preferences for a given user for a given team
    Trigger appropriate notification channel for the given incident
    """
    user = User.objects.get(id=user_id)
    email = User.email
    team = Team.objects.get(id=team_id)
    if TeamAssignment.objects.filter(user=user, team=team).exists():
        assignment = TeamAssignment.objects.get(user=user, team=team)
        if priority == "Low":
            if assignment.notify_via_email_low_priority:
                send_email_notification(
                    email=email,
                    incident_id=incident_id,
                )
            if assignment.notify_via_phone_low_priority:
                send_text_notification(
                    phone_number=user.phone_number,
                    incident_id=incident_id,
                )
            if assignment.notify_via_webhooks_low_priority:
                send_webhook_notification(
                    webhook_url=assignment.webhook_url,
                    incident_id=incident_id,
                )
        else:
            if assignment.notify_via_email_high_priority:
                send_email_notification(
                    email=email,
                    incident_id=incident_id,
                )
            if assignment.notify_via_phone_high_priority:
                send_text_notification(
                    phone_number=user.phone_number,
                    incident_id=incident_id,
                )
            if assignment.notify_via_webhooks_high_priority:
                send_webhook_notification(
                    webhook_url=assignment.webhook_url,
                    incident_id=incident_id,
                )


@app.task
def notify_team(team_id, incident_id, priority="Low"):
    """
    Notify all the members of the team, regarding the incident
    """
    team = Team.objects.get(id=team_id)
    for user in team.users:
        notify_user(
            user_id=user.id,
            team_id=team_id,
            incident_id=incident_id,
            priority=priority,
        )
