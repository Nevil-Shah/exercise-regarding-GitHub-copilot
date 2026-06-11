"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
import os
import re
import socket
from pathlib import Path
import uvicorn

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

class ParticipantRequest(BaseModel):
    email: str

    @field_validator('email')
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
        if not re.match(pattern, value):
            raise ValueError('Invalid email format')
        return value

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
    ,
    "Soccer Club": {
        "description": "Outdoor soccer practices and matches",
        "schedule": "Wednesdays and Saturdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Basketball Team": {
        "description": "Competitive basketball training and games",
        "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Art Club": {
        "description": "Painting, drawing, and mixed media workshops",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Acting, stagecraft, and school productions",
        "schedule": "Fridays, 4:00 PM - 6:30 PM",
        "max_participants": 25,
        "participants": []
    },
    "Debate Team": {
        "description": "Argue current topics and build public speaking skills",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Robotics Club": {
        "description": "Design and build robots for competitions",
        "schedule": "Saturdays, 9:00 AM - 12:00 PM",
        "max_participants": 12,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


def get_activity(activity_name: str):
    if not activity_name or activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, payload: ParticipantRequest):
    """Sign up a student for an activity"""
    activity = get_activity(activity_name)
    normalized_email = payload.email.strip().lower()
    existing = [p.strip().lower() for p in activity.get("participants", [])]

    if normalized_email in existing:
        raise HTTPException(status_code=400, detail="Student already registered for this activity")

    max_p = activity.get("max_participants")
    if isinstance(max_p, int) and len(existing) >= max_p:
        raise HTTPException(status_code=400, detail="Activity is full")

    activity.setdefault("participants", []).append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def remove_participant(activity_name: str, payload: ParticipantRequest):
    """Unregister a student from an activity"""
    activity = get_activity(activity_name)
    normalized_email = payload.email.strip().lower()
    existing = [p.strip().lower() for p in activity.get("participants", [])]

    if normalized_email not in existing:
        raise HTTPException(status_code=404, detail="Participant not found in activity")

    activity["participants"] = [p for p in activity.get("participants", []) if p.strip().lower() != normalized_email]
    return {"message": f"Removed {normalized_email} from {activity_name}"}


def find_available_port(start_port: int = 8000, max_port: int = 8100) -> int:
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("0.0.0.0", port)) != 0:
                return port
    raise RuntimeError(f"No available port found in range {start_port}-{max_port}")


if __name__ == "__main__":
    port = find_available_port(8000, 8100)
    if port != 8000:
        print(f"Port 8000 is busy, starting on port {port} instead.")
    uvicorn.run(app, host="0.0.0.0", port=port)
