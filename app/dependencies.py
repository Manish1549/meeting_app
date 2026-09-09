from repositories.in_memory_appointment_repository import (
    InMemoryAppointmentRepository
)
from services.availability_service import AvailabilityService
from services.appointment_service import AppointmentService


appointment_repository = InMemoryAppointmentRepository()

availability_service = AvailabilityService(appointment_repository)

appointment_service = AppointmentService(
    appointment_repository,
    availability_service
)