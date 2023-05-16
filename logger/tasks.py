import re
import os
import requests
from core.celery import app
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from twilio.rest import Client
from django.conf import settings
from uuid import uuid4
from urllib.parse import urlencode
from incident.models import EscalationLevelAssignment, Webhook
from logger.models import Endpoint, Service, Log, Incident
from incident.tasks import create_incident
from django.template.loader import render_to_string

from users.models import UserGroups, User
from users.tasks import notify_user

# disable SSL warnings: handshakes are computationally expensive, could drop that overhead
requests.urllib3.disable_warnings()


def build_path(date):
    """
    Builds a unique pathname using the given date
    """
    filename = date.strftime("%Y-%m-%d-%H-%M-%S-") + str(uuid4()) + ".png"
    path = f"media/incidents/{filename}"
    return path


def get_screenshot(url=None, path=None, folder="media/", filename="screenshot.png"):
    """
    Gets a screenshot using APIFlash
    """
    if path is None:
        path = f"{folder}/{filename}"

    params = {
        "access_key": os.environ.get("API_FLASH_KEY"),
        "url": f"{url}",
        "full_page": True,
        "scroll_page": True,
        "fresh": True,
    }

    url = "https://api.apiflash.com/v1/urltoimage?" + urlencode(params)

    response = requests.get(url)

    with open(f"{path}", "wb") as f:
        f.write(response.content)

    return response.status_code


@app.task
def add_screenshot_to_log(incident_id, url):
    """
    Adds a screenshot to the logs
    """
    incident = Incident.objects.get(pk=incident_id)
    url = url
    path = build_path(incident.created_at)
    incident.source = (
        "https://media.giphy.com/media/etOX3h7ApZuDe7Fc5w/giphy-downsized-large.gif"
    )
    try:
        if get_screenshot(url, path) != 200:
            incident.source = path
    except requests.exceptions.ReadTimeout as errrt:
        pass
    except requests.exceptions.RequestException as errex:
        pass
    finally:
        incident.save()


@app.task
def process_endpoint(endpoint):
    """
    Get response time
    Get "OK or Down or Unknown" status
    """
    response_time = -1
    match = False
    message = ""
    context = {}
    response = None
    try:
        headers = (
            {
                endpoint.request_handler.header_name: endpoint.request_handler.header_value
            }
            if endpoint.request_handler.header_name
            and endpoint.request_handler.header_value
            else {}
        )
        body = endpoint.request_handler.body if endpoint.request_handler.body else {}
        auth = (
            (
                endpoint.request_handler.auth_username,
                endpoint.request_handler.auth_password,
            )
            if endpoint.request_handler.auth_username
            and endpoint.request_handler.auth_password
            else None
        )

        response = requests.request(
            method=endpoint.request_handler.method,
            url=endpoint.url,
            headers=headers,
            data=body,
            auth=auth,
            timeout=endpoint.timeout,
            verify=endpoint.request_handler.verify_ssl,
        )

        response_time = response.elapsed.total_seconds()

        regex = endpoint.regex

        match = (
            re.search(regex, str(response.status_code))
            if endpoint.logger_type == "status"
            else re.search(regex, str(response.content))
        )

        message = "Request sent successfully."

    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        message = "Request timed out. Try exceeding the timeout limit."
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        message = "Request exceeds the configured number of maximum redirections. Try a different URL."
    except requests.exceptions.ConnectionError:
        # Network problem (DNS failure, refused connection, etc)
        message = "Request couldn't be fulfilled. URL connection refused."
    except requests.exceptions.HTTPError:
        # Invalid HTTP response or regular unsuccesful
        message = "HTTP response is invalid. Please try with a different URL."
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        message = "Request couldn't be fulfilled. URL connection refused."
    finally:
        # prepare a context object
        context = {
            "response_time": response_time,
            "status": "UP" if match else "DOWN",
            "message": message,
        }

        if not match:
            context["response_body"] = response
            # TODO: prepare a screenshot queue

    return context


@app.task
def prepare_logs(frequency=180):
    """
    Optimized : Prepares all the endpoints which have the given frequency
    """
    services = Service.objects.filter(is_active=True)

    # Instead of creating each Log instance individually in a loop, can use the bulk_create() method to create multiple instances in a single database query
    log_instances = []
    for service in services:
        for endpoint in service.endpoints.filter(check_frequency=frequency):
            # TODO: decouple request queue for longer timeouts etc.
            # TODO: figure out a fix, some queues could be overwhelmed by request volume
            # TODO: automatically resolve incidents after a given recovery period
            result = process_endpoint(endpoint)
            status = result.get("status", "UP")
            if status == "DOWN":
                # create new incident
                create_incident.delay(service_id=service.id)
            log = Log(
                response_time=result.get("response_time", 0),
                status=status,
                message=result.get("message"),
                entity_type=ContentType.objects.get_for_model(Endpoint),
                entity_id=endpoint.pk,
            )
            response_body = result.get("response_body", None)
            if response_body is not None:
                log.response_body = response_body
            log_instances.append(log)
    Log.objects.bulk_create(log_instances)


@app.task
def send_email_notification(email, incident_id):
    """
    Notify via email notification
    """
    sender = os.environ.get("AWS_SES_EMAIL_SENDER", "no-reply@watchover.dev")

    incident = Incident.objects.get(id=incident_id)

    send_mail(
        subject=f"An Incident requires your attention - Status {incident.status}",
        message=f"Service Name: {incident.service}\n View Details: {incident.get_detail_view()})",
        from_email=sender,
        recipient_list=email,
    )


@app.task
def send_text_notification(phone_number, incident_id):
    """
    Notify user via text.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    incident = Incident.objects.get(id=incident_id)

    body = f"An Incident requires your attention - Status {incident.status}\nService Name: {incident.service}\nView Details: {incident.get_details()}"

    client.messages.create(
        to=str(phone_number),
        from_=f"{settings.TWILIO_NUMBER}",
        body=f"{body}",
    )


@app.task
def send_webhook_notification(webhook_url, incident_id):
    incident = Incident.objects.get(id=incident_id)
    payload = incident.get_dict()
    status_code = 500
    try:
        response = requests.post(
            url=webhook_url,
            json=payload,
        )
        status_code = response.status_code
        message = "Request sent successfully."

    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        message = "Request timed out. Try exceeding the timeout limit."
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        message = "Request exceeds the configured number of maximum redirections. Try a different URL."
    except requests.exceptions.ConnectionError:
        # Network problem (DNS failure, refused connection, etc)
        message = "Request couldn't be fulfilled. URL connection refused."
    except requests.exceptions.HTTPError:
        # Invalid HTTP response or regular unsuccesful
        message = "HTTP response is invalid. Please try with a different URL."
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        message = "Request couldn't be fulfilled. URL connection refused."
    finally:
        # prepare a context object
        context = {
            "status_code": status_code,
            "message": message,
        }

    return context


def notify_user_groups(
    user_group_id,
    team_id,
    incident_id,
    priority="Low",
):
    user_group = UserGroups.objects.get(id=user_group_id)
    for user in user_group.users.all():
        notify_user(
            user_id=user.id,
            team_id=team_id,
            incident_id=incident_id,
            priority=priority,
        )


def escalate_incident(incident_id, priority):
    incident = Incident.objects.get(incident_id=incident_id)
    service = incident.service
    policy = service.policy
    level = incident.escalation_level
    escalation_level = EscalationLevelAssignment.objects.get(
        policy=policy, level=level
    )[0].level

    for action in escalation_level.actions.all():
        entity_id = action.entity_id
        entity_type = action.entity_type

        if entity_type == ContentType.objects.get_for_model(User):
            notify_user(
                user_id=entity_id,
                team_id=service.team.id,
                incident_id=incident_id,
                priority=priority,
            )
        elif entity_type == ContentType.objects.get_for_model(UserGroups):
            notify_user_groups(
                user_group_id=entity_id,
                team_id=service.team.id,
                incident_id=incident_id,
                priority=priority,
            )
        elif entity_type == ContentType.objects.get_for_model(Webhook):
            webhook_url = Webhook.objects.get(id=entity_id).url
            send_webhook_notification(
                webhook_url=webhook_url,
                priority=priority,
            )

    incident.escalation_level += 1
    incident.save()
