from models.appointment import Appointment
from abc import ABC, abstractmethod
from datetime import datetime, date
from models.appointment_status import AppointmentStatus
class AppointmentRepository(ABC):
    @abstractmethod
    def save(self, appointment: Appointment) -> Appointment:
        pass

    @abstractmethod
    def get_appointment_by_id(self, appointment_id: int) -> Appointment|None:
        pass

    @abstractmethod
    def update_appointment(self, appointment: Appointment) -> Appointment:
        pass

    @abstractmethod
    def list_appointments(self,appointment_date :date |None = None,
                          status : AppointmentStatus|None = None) -> list[Appointment]:
        pass

    @abstractmethod
    def find_overlapping_appointments(self,
                                       start_time: datetime,
                                       end_time: datetime,
                                        exclude_appointment_id: int | None = None
                                       ) -> list[Appointment]:
        pass
