import re
import os
import requests
from core.celery import app
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from twilio.rest import Client
from django.conf import settings
from logger.models import Endpoint, Service, Log, Incident
from users.models import User
from incident.tasks import create_incident
from django.template.loader import render_to_string

# disable SSL warnings: handshakes are computationally expensive, could drop that overhead
requests.urllib3.disable_warnings()


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


def incident_builder(incident_id):
    """
    Build a incident dictionary for a given incident
    """
    incident = Incident.objects.get(id=incident_id)
    title = incident.title
    body = incident.description
    priority = incident.priority

    # TODO: reverse the incident detail view
    detail_view = ""
    # TODO: reverse the incident acknowledgement
    acknowledgement_view = ""

    context = {
        "id": incident_id,
        "title": title,
        "body": body,
        "priority": priority,
        "status": incident.status,
        "detail_view": detail_view,
        "acknowledgement_view": acknowledgement_view,
    }

    return context


@app.task
def notify_via_email(email, intent, context):
    """
    Notify via email notification
    """
    sender = os.environ.get("AWS_SES_EMAIL_SENDER", "no-reply@watchover.dev")

    email_context = context
    if intent == "Alert":
        email_context.pop("acknowledgement_view")

    email_body = render_to_string("email_template.html", email_context)

    send_mail(
        f"Incident ID {context.get('id')}:{context.get('status')}",
        f"{email_body}",
        f"{sender}",
        [f"{email}"],
    )


@app.task
def notify_via_text(phone_number, intent, context):
    """
    Notify user via text.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    body = f"Incident ID {context.get('id')}:{context.get('status')}"

    if intent == "Resolve":
        body += f"\nAcknowledge: {context.get('acknowledgement_view')}"

    client.messages.create(
        to=str(phone_number),
        from_=f"{settings.TWILIO_NUMBER}",
        body=f"{body}",
    )


@app.task
def trigger_webhook(webhook_url, context, intent):
    payload = context
    status_code = 500
    if intent == "Alert":
        payload.pop("acknowledgement_view")
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
