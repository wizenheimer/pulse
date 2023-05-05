from decouple import config
from google.oauth2 import service_account
import googleapiclient.discovery
import datetime

CAL_ID = config("CAL_ID")
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "./google-credentials.json"


def add_on_call(
    email,
    start_date,
    day=0,
    min=0,
    sec=0,
    timezone="utc",
):
    """
    Add a new event to Google Calendar
    start date = %d:%m:%y %H:%M:%S
    day: integer, optional
    min: integer, optional
    sec: integer, optional
    timezone: string, default="utc"
    """
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = googleapiclient.discovery.build("calendar", "v3", credentials=credentials)

    # create a new event
    new_event = {
        "summary": f"{email}",
        # "location": "",
        "description": "On Call",
        "start": {
            "date": f"{datetime.strptime(start_date, '%d:%m:%y %H:%M:%S')}",
            "timeZone": f"{timezone}",
        },
        "end": {
            "date": f"{datetime.strptime(start_date, '%d:%m:%y %H:%M:%S') + datetime.timedelta(days=day, minutes=min, seconds=sec)}",
            "timeZone": f"{timezone}",
        },
    }
    service.events().insert(calendarId=CAL_ID, body=new_event).execute()
