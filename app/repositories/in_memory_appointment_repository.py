from models.appointment import Appointment
from models.appointment_status import AppointmentStatus
from repositories.appointment_repository import AppointmentRepository
from datetime import datetime, date

class InMemoryAppointmentRepository(AppointmentRepository):
    def __init__(self):
        self.appointments: dict[int, Appointment] = {} 
        # appointments: dict[int, Appointment]
    def save(self, appointment: Appointment) -> Appointment:
        appointment.appointment_id = len(self.appointments) + 1
        self.appointments[appointment.appointment_id] = appointment
        return appointment

    def get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
        return self.appointments.get(appointment_id)

    def update_appointment(self, appointment: Appointment) -> Appointment:
        if appointment.appointment_id in self.appointments:
            self.appointments[appointment.appointment_id] = appointment
            return appointment
        else:
            raise ValueError(f"Appointment with ID {appointment.appointment_id} does not exist.")   

    def list_appointments(self, appointment_date: date | None = None, status: AppointmentStatus | None = None) -> list[Appointment]:
        result = list(self.appointments.values())
        if appointment_date is not None:
            result = [appt for appt in result if appt.start_time.date() == appointment_date]
        if status is not None:
            result = [appt for appt in result if appt.status == status]
        return result 
    def find_overlapping_appointments(self, start_time: datetime, end_time: datetime, exclude_appointment_id: int | None = None) -> list[Appointment]:
        overlapping_appointments = []
        for appointment in self.appointments.values():
            if exclude_appointment_id is not None and appointment.appointment_id == exclude_appointment_id:
                continue
            if appointment.status == AppointmentStatus.CANCELLED:
                continue
            if (appointment.start_time < end_time and appointment.end_time > start_time):
                overlapping_appointments.append(appointment)
        return overlapping_appointments     