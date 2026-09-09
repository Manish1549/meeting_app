from datetime import datetime
from pydantic import BaseModel

from models.appointment_status import AppointmentStatus

class CreateAppointmentRequest(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime

class UpdateAppointmentRequest(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime

class AppointmentResponse(BaseModel):
    appointment_id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime
    status: AppointmentStatus

