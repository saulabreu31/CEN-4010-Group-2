from models import db, CalendarEvent
from datetime import datetime

def add_event(user_id, title, description, start_time, end_time):
    """Add a new event to the calendar."""
    new_event = CalendarEvent(
        user_id=user_id,
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(new_event)
    db.session.commit()
    return {"message": "Event added successfully"}

def get_events(user_id):
    """Retrieve all events for a specific user."""
    events = CalendarEvent.query.filter_by(user_id=user_id).all()
    return events

def update_event(event_id, title=None, description=None, start_time=None, end_time=None):
    """Update an existing event."""
    event = CalendarEvent.query.get(event_id)
    if event:
        if title:
            event.title = title
        if description:
            event.description = description
        if start_time:
            event.start_time = start_time
        if end_time:
            event.end_time = end_time
        db.session.commit()
        return {"message": "Event updated successfully"}
    return {"error": "Event not found"}

def delete_event(event_id):
    """Delete an event."""
    event = CalendarEvent.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        return {"message": "Event deleted successfully"}
    return {"error": "Event not found"}
