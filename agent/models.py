from pydantic import BaseModel


class CalendarEvent(BaseModel):
    name: str
    description: str
