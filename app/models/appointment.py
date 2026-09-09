from datetime import datetime
from models.appointment_status import AppointmentStatus



class Appointment:
    def __init__(self, title: str, description: str, start_time: datetime, end_time: datetime, created_at: datetime, updated_at: datetime, status: AppointmentStatus, appointment_id :int|None = None):
        self.appointment_id = appointment_id
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = created_at
        self.updated_at = updated_at
        self.status = status