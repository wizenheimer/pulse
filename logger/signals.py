from django.db.models import signals
from django.dispatch import receiver
from users.models import User, TeamAssignment
from util.calendar_util import get_on_call
from .models import Incident, TeamAssignment
from .tasks import notify_via_email, notify_via_text, trigger_webhook, incident_builder


def notify_on_call(email, service, priority, context):
    """
    Figure out the preferences for the given user
    Prepare on-call resolutions accordingly
    """
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        teams = service.teams.filter()
        for team in teams:
            if TeamAssignment.objects.filter(team=team, user=user).exists():
                assignment = TeamAssignment.objects.get(user=user, team=team)
                # figure out the notification preferences for the user for the given priority
                # trigger notification asynchronously
                if priority == "Low":
                    if assignment.notify_via_email_low_priority:
                        notify_via_email(
                            email=email,
                            intent="Resolve",
                            context=context,
                        )
                    if assignment.notify_via_phone_low_priority:
                        notify_via_text(
                            phone_number=user.phone_number,
                            intent="Resolve",
                            context=context,
                        )
                    if assignment.notify_via_webhooks_low_priority:
                        trigger_webhook(
                            webhook_url=assignment.webhook_url,
                            context=context,
                            intent="Resolve",
                        )
                else:
                    if assignment.notify_via_email_high_priority:
                        notify_via_email(
                            email=email,
                            intent="Resolve",
                            context=context,
                        )
                    if assignment.notify_via_phone_high_priority:
                        notify_via_text(
                            phone_number=user.phone_number,
                            intent="Resolve",
                            context=context,
                        )
                    if assignment.notify_via_webhooks_high_priority:
                        trigger_webhook(
                            webhook_url=assignment.webhook_url,
                            context=context,
                            intent="Resolve",
                        )

        # TODO: check if email is part of secondary field
    else:
        # User is not part of the team
        notify_via_email(
            email=email,
            intent="Resolve",
            context=context,
        )
        # TODO: send an invite via email


@receiver(signals.post_save, sender=Incident)
def escalation_builder(sender, instance, created, **kwargs):
    """
    Prepare Level 0 escalation
    """
    if created:
        service = instance.service
        calendar = service.calendar
        context = incident_builder(instance)
        on_call = get_on_call(
            url=calendar.url,
            timezone=calendar.timezone,
        )
        for email in on_call:
            notify_on_call(
                email,
                service,
                instance.priority,
                context,
            )
