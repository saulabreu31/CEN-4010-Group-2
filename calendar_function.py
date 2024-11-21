from models import db, CalendarEvent
from datetime import datetime
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_events(user_id):
    """Retrieve all events for a specific user."""
    try:
        logger.debug(f"Fetching events for user {user_id}")


        # Convert user_id to int if it's a string
        try:
            user_id = int(user_id)
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid user_id format: {str(e)}")
            return {"error": "Invalid user ID format"}


        # Query events
        events = CalendarEvent.query.filter_by(user_id=user_id).all()
        logger.debug(f"Found {len(events)} events")


        # Convert events to dictionary
        events_list = []
        for event in events:
            try:
                events_list.append({
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "start_time": event.start_time.isoformat() if event.start_time else None,
                    "end_time": event.end_time.isoformat() if event.end_time else None
                })
            except Exception as e:
                logger.error(f"Error converting event {event.id}: {str(e)}")
                continue


        return events_list


    except Exception as e:
        logger.error(f"Error in get_events: {str(e)}")
        return {"error": str(e)}


def add_event(user_id, title, description, start_time, end_time):
    """Add a new event to the calendar."""
    try:
        logger.debug(f"Adding event: {title} for user {user_id}")
        logger.debug(f"Start time: {start_time}, End time: {end_time}")


        # Convert user_id to int if it's a string
        try:
            user_id = int(user_id)
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid user_id format: {str(e)}")
            return {"error": "Invalid user ID format"}


        new_event = CalendarEvent(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time
        )


        db.session.add(new_event)
        db.session.commit()


        logger.debug(f"Successfully added event with ID: {new_event.id}")


        return {
            "success": True,
            "message": "Event added successfully",
            "event": {
                "id": new_event.id,
                "user_id": new_event.user_id,
                "title": new_event.title,
                "description": new_event.description,
                "start_time": new_event.start_time.isoformat(),
                "end_time": new_event.end_time.isoformat()
            }
        }


    except Exception as e:
        logger.error(f"Error in add_event: {str(e)}")
        db.session.rollback()
        return {"error": str(e)}




def delete_event(event_id):
    """Delete a specific calendar event."""
    try:
        logger.debug(f"Attempting to delete event with ID: {event_id}")


        # Find the event
        event = CalendarEvent.query.get(event_id)


        if not event:
            logger.error(f"Event with ID {event_id} not found")
            return {"error": "Event not found", "success": False}


        # Delete the event
        db.session.delete(event)
        db.session.commit()


        logger.debug(f"Successfully deleted event with ID: {event_id}")
        return {"success": True, "message": "Event deleted successfully"}


    except Exception as e:
        logger.error(f"Error in delete_event: {str(e)}")
        db.session.rollback()
        return {"error": str(e), "success": False}