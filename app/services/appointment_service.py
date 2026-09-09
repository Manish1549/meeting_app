from datetime import datetime, date

from models.appointment import Appointment
from models.appointment_status import AppointmentStatus
from repositories.appointment_repository import AppointmentRepository
from services.availability_service import AvailabilityService
from exceptions import AppointmentConflictError, AppointmentNotFoundError 

class AppointmentService:

    def __init__(
        self,
        repository: AppointmentRepository,
        availability_service: AvailabilityService
    ):
        self.repository = repository
        self.availability_service = availability_service

    def create_appointment(self, title: str, description: str, start_time: datetime, end_time: datetime) -> Appointment:

        if not self.availability_service.is_available(start_time, end_time):
           raise AppointmentConflictError("The requested time slot is not available.")
        appointment = Appointment(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=AppointmentStatus.SCHEDULED
        )
        return self.repository.save(appointment)

    def update_appointment(self, appointment_id: int, title: str, description: str, start_time: datetime, end_time: datetime) -> Appointment:
        appointment = self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(
                      f"Appointment with ID {appointment_id} does not exist."
                        )

        if not self.availability_service.is_available(start_time, end_time, exclude_appointment_id=appointment_id):
            raise AppointmentConflictError("The requested time slot is not available.")

        appointment.title = title
        appointment.description = description
        appointment.start_time = start_time
        appointment.end_time = end_time
        appointment.updated_at = datetime.now()

        return self.repository.update_appointment(appointment)
    def cancel_appointment(self, appointment_id: int) -> None:
        appointment = self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(f"Appointment with ID {appointment_id} does not exist.")
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise AppointmentConflictError(f"Only scheduled appointments can be cancelled. Current status: {appointment.status.value}")

        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.now()
        self.repository.update_appointment(appointment)

    def complete_appointment(self, appointment_id: int) -> None:
        appointment = self.repository.get_appointment_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(f"Appointment with ID {appointment_id} does not exist.")
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise AppointmentConflictError(f"Only scheduled appointments can be completed. Current status: {appointment.status.value}")
        appointment.status = AppointmentStatus.COMPLETED
        appointment.updated_at = datetime.now()
        self.repository.update_appointment(appointment)   

    def list_appointments(self, appointment_date: date | None = None, status: AppointmentStatus | None = None) -> list[Appointment]:
        return self.repository.list_appointments(appointment_date, status)     
    


