import os
import json
from datetime import datetime

class NoteTakingSystem:
    def __init__(self, storage_dir="notes"):
        """
        Initialize the note-taking system with a storage directory.

        :param storage_dir: Directory where notes will be saved.
        """
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def create_note(self, course_name, note_title, content):
        """
        Create a new note for a specific course.

        :param course_name: Name of the course.
        :param note_title: Title of the note.
        :param content: Content of the note.
        :return: Dictionary with success message and note details.
        """
        try:
            course_dir = os.path.join(self.storage_dir, course_name)
            os.makedirs(course_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            note_filename = f"{note_title}_{timestamp}.json"
            note_path = os.path.join(course_dir, note_filename)

            note_data = {
                "course_name": course_name,
                "note_title": note_title,
                "content": content,
                "timestamp": timestamp
            }

            with open(note_path, "w") as note_file:
                json.dump(note_data, note_file, indent=4)

            return {"message": "Note created successfully", "note_path": note_path}

        except Exception as e:
            return {"error": f"Failed to create note: {str(e)}"}

    def view_notes(self, course_name):
        """
        View all notes for a specific course.

        :param course_name: Name of the course.
        :return: List of notes (title and timestamp).
        """
        try:
            course_dir = os.path.join(self.storage_dir, course_name)
            if not os.path.exists(course_dir):
                return {"notes": [], "message": "No notes found for this course."}

            notes = []
            for note_file in os.listdir(course_dir):
                if note_file.endswith(".json"):
                    note_path = os.path.join(course_dir, note_file)
                    with open(note_path, "r") as file:
                        note_data = json.load(file)
                        notes.append({
                            "title": note_data["note_title"],
                            "timestamp": note_data["timestamp"],
                            "path": note_path
                        })

            return {"notes": notes}

        except Exception as e:
            return {"error": f"Failed to retrieve notes: {str(e)}"}

    def read_note_content(self, note_path):
        """
        Read the content of a specific note.

        :param note_path: Path to the note file.
        :return: Content of the note or an error message.
        """
        try:
            if not os.path.exists(note_path):
                return {"error": "Note does not exist."}

            with open(note_path, "r") as file:
                note_data = json.load(file)
                return {"content": note_data}

        except Exception as e:
            return {"error": f"Failed to read note: {str(e)}"}

    def delete_note(self, note_path):
        """
        Delete a specific note.

        :param note_path: Path to the note file.
        :return: Success or error message.
        """
        try:
            if os.path.exists(note_path):
                os.remove(note_path)
                return {"message": "Note deleted successfully."}
            return {"error": "Note does not exist."}

        except Exception as e:
            return {"error": f"Failed to delete note: {str(e)}"}
