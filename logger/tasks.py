import re
import requests
from core.celery import app
from logger.models import Endpoint, Service, Log
from django.contrib.contenttypes.models import ContentType

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
    # TODO: figure out a workaround for using signals, signals won't be triggered in case of bulk create operation
    # TODO: try to reuse the services query set, maybe operating on stale state
    services = Service.objects.filter(is_active=True)

    # Instead of creating each Log instance individually in a loop, can use the bulk_create() method to create multiple instances in a single database query
    log_instances = []
    for service in services:
        for endpoint in service.endpoints.filter(check_frequency=frequency):
            # TODO: decouple request queue for longer timeouts etc.
            # TODO: figure out a fix, some queues could be overwhelmed by request volume
            result = process_endpoint(endpoint)
            status = result.get("status", "UP")
            # TODO:
            # if status is "DOWN":
            #     create new incident
            #     pass
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
