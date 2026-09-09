from datetime import datetime
from exceptions import InvalidAppointmentTimeError
from repositories import appointment_repository
from repositories.appointment_repository import AppointmentRepository


class AvailabilityService:
    def __init__(self, repository: AppointmentRepository):
        self.repository =   repository

    def is_available(self, start_time: datetime, end_time: datetime, exclude_appointment_id :int |None=None)->bool:
        if start_time >= end_time:
             raise InvalidAppointmentTimeError(
                      "Start time must be before end time."
                           )
        overlapping_appointments = self.repository.find_overlapping_appointments(start_time, end_time, exclude_appointment_id)
        return len(overlapping_appointments) == 0