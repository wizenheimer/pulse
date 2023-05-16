from django.db.models import signals
from django.dispatch import receiver
from users.tasks import notify_user
from logger.tasks import send_email_notification
from .models import Incident
from users.models import User


@receiver(signals.post_save, sender=Incident)
def escalation_builder(sender, created, instance, **kwargs):
    if created:
        service = instance.service
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

    return instance
