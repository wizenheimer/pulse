import requests
import pytz
import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [
        ".yaml",
    ]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")


def validate_timezone(value):
    """
    Validate a given timezone
    """
    try:
        pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValidationError("Invalid timezone.")


def validate_icalendar_url(icalendar_url):
    """
    Validate icalendar url, using requests module
    """
    url = "https://icalendar.org/validator.html"
    params = {
        "url": f"{icalendar_url}",
        "json": "1",
    }

    try:
        response = requests.get(url, params=params)
        # Raises an exception for 4XX/5XX status codes
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # error occurred
        raise ValidationError("Couldn't validate iCalendar URL")
