import threading
from langchain.tools import tool
from datetime import datetime
from typing import Any
from googleapiclient.errors import HttpError
from utils.g_calendar import get_credentials, setup_google_calendar_service

creds = get_credentials()
_local = threading.local()


def get_service():
    # The agent runs parallel tool calls on separate threads, and httplib2
    # connections aren't thread-safe, so each thread gets its own client.
    if not hasattr(_local, "service"):
        _local.service = setup_google_calendar_service(creds)
    return _local.service


@tool
def get_events(start_time: datetime, end_time: datetime) -> dict[str, list[dict[str, Any]]]:
    """ Fetches events from the user's primary calendar between start_time
    and end_time
    """
    # The API needs RFC 3339 timestamps with a timezone; naive datetimes are
    # treated as local time.
    time_min = start_time.astimezone().isoformat()
    time_max = end_time.astimezone().isoformat()
    events_result = (
        get_service().events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            maxResults=None,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    return {
        "events": [
            {
                "id": e["id"],
                "summary": e.get("summary", ""),
                "start": {
                    "dateTime": e["start"].get("dateTime"),
                    "date": e["start"].get("date"),
                    "timeZone": e["start"].get("timeZone"),
                },
                "end": {
                    "dateTime": e["end"].get("dateTime"),
                    "date": e["end"].get("date"),
                    "timeZone": e["end"].get("timeZone"),
                }
            }
            for e in events
        ]
    }


@tool
def add_event(
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: str = "",
) -> dict[str, Any]:
    """Adds an event to the user's primary calendar.

    Args:
        summary: The title of the event.
        start_time: When the event starts, as an ISO 8601 datetime with a
            timezone offset, e.g. 2026-09-27T05:00:00-04:00.
        end_time: When the event ends, in the same format. If the user gives
            no duration, use one hour after start_time.
        description: Optional longer notes for the event.

    Returns the created event's id and a link to it. Google generates the id.
    """
    body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time.astimezone().isoformat()},
        "end": {"dateTime": end_time.astimezone().isoformat()},
    }
    try:
        event = (
            get_service().events()
            .insert(calendarId="primary", body=body)
            .execute(num_retries=2)
        )
    except (HttpError, TimeoutError) as error:
        # Return the error to the model instead of crashing the agent loop,
        # so it can fix its arguments and retry or tell the user.
        return {"error": str(error)}

    return {"id": event["id"], "link": event.get("htmlLink")}
