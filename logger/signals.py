from django.db.models import signals
from django.dispatch import receiver
from users.tasks import notify_user, notify_team
from logger.tasks import send_email_notification, escalate_incident
from .models import Incident, Log
from users.models import User


@receiver(signals.post_save, sender=Incident)
def level_0_escalation(sender, created, instance, **kwargs):
    if created:
        service = instance.service
        instance.escalation_level = 1
        team_id = service.team.id
        on_call_list = service.calendar.get_on_call()
        for email in on_call_list:
            if User.objects.filter(email=email).exists():
                user_id = User.objects.get(email=email).id
                notify_user(
                    user_id=user_id,
                    team_id=team_id,
                    incident_id=instance.id,
                    priority=instance.priority,
                )
            else:
                send_email_notification(
                    email=email,
                    incident_id=instance.id,
                )
        instance.save()
    else:
        service = instance.service
        policy = service.escalation_policy
        if instance.status == "Open":
            team_id = service.team.id
            max_level = policy.max_level
            if instance.escalation_level == max_level and policy.notify_all:
                notify_team(
                    team_id=team_id,
                    incident_id=instance.id,
                    priority=instance.priority,
                )
            else:
                escalate_incident(
                    incident_id=instance.id,
                    priority=instance.priority,
                )

    return instance
