from datetime import datetime, timedelta
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth import get_credentials

def parse_shift(shift):
    date_str = shift[0].split(" ")[1]
    date_str = date_str.rstrip(".")
    day, month = date_str.split(".")
    year = datetime.now().year

    time_str = shift[1]
    time_str = time_str.replace("–", "-")
    start_str, end_str = time_str.split("-")

    tz = pytz.timezone("Europe/Helsinki")

    start_dt = tz.localize(datetime(year, int(month), int(day),
                int(start_str.split(":")[0]), int(start_str.split(":")[1])))

    end_dt = tz.localize(datetime(year, int(month), int(day),
                int(end_str.split(":")[0]), int(end_str.split(":")[1])))

    if end_dt < start_dt:
        end_dt += timedelta(days=1)

    return start_dt, end_dt

def event_exists(service, start_dt, end_dt, summary):
    existing = service.events().list(
        calendarId="primary",
        timeMin=start_dt.isoformat(),
        timeMax=end_dt.isoformat(),
        singleEvents=True
    ).execute()

    for event in existing.get("items", []):
        if event.get("summary") == summary:
            return True
    return False
  
def create_shift_event(service, shift):
  start_dt, end_dt = parse_shift(shift)

  timezone = pytz.timezone("Europe/Helsinki")
  now = datetime.now(timezone)

  if start_dt < now:
     print(f"Skipping past shift: {shift[0]} {shift[1]}")
     return

  if event_exists(service, start_dt, end_dt, shift[2]):
     print(f"Skipping duplicate: {shift[0]} {shift[1]}")
     return

  event = {
    "summary": shift[2],                 # "Työ"
    "colorId": "2",
    "start": {
        "dateTime": start_dt.isoformat(),
        "timeZone": "Europe/Helsinki"
        },
    "end": {
        "dateTime": end_dt.isoformat(),
        "timeZone": "Europe/Helsinki"
        }
    }

  created = service.events().insert(calendarId="primary", body=event).execute()
  print(f"Event created: {created.get('htmlLink')}")

def add_shifts_to_calendar(shifts):
  creds = get_credentials()
  service = build("calendar", "v3", credentials=creds)

  #shifts = [
  #  ['Ti 10.3.', '16:00–21:30', 'Työ'],
  #  ["Sun 15.3.", "15:15-18:00", "Työ"],
  #  ["Sun 1.3.", "15:15-18:00", "Työ"]
  #  # ... rest of your shifts
  #]

  for shift in shifts:
    create_shift_event(service, shift)

#if __name__ == "__main__":
  #main()