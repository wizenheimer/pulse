from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import test_port, test_uptime, test_ssl, test_website_speed
from .models import MonitorResult, Monitor


@receiver(post_save, sender=Monitor)
def trigger_monitors(sender, created, instance, **kwargs):
    if created:
        if instance.test_uptime:
            "Perform uptime tests"
            result = MonitorResult.objects.create(monitor=instance)
            result.type = "Uptime Monitor Result"
            ping = test_uptime(instance.url, instance.timeout)
            print(ping)
            result.status_code = ping["status_code"]
            result.log = ping["log"]
            result.save()
        if instance.test_port:
            "Perform port tests"
            result = MonitorResult.objects.create(monitor=instance)
            result.type = "Port Monitor Result"
            ping = test_port(instance.url, instance.port)
            result.status_code = ping["status_code"]
            result.log = ping["log"]
            result.save()
        if instance.test_ssl:
            "Perform ssl tests"
            result = MonitorResult.objects.create(monitor=instance)
            result.type = "SSL Monitor Result"
            ping = test_ssl(instance.url)
            result.status_code = ping["status_code"]
            result.log = ping["log"]
            result.save()
        if instance.test_speed:
            "Perform speed tests"
            result = MonitorResult.objects.create(monitor=instance)
            result.type = "Speed Monitor Result"
            ping = test_website_speed(instance.url, instance.timeout)
            result.status_code = ping["status_code"]
            result.log = ping["log"]
            result.response_time = ping["response_time"]
            result.save()
    return instance
