from datetime import datetime, timedelta

from repositories.in_memory_appointment_repository import InMemoryAppointmentRepository
from services.availability_service import AvailabilityService
from services.appointment_service import AppointmentService
from models.appointment_status import AppointmentStatus


def test_create_appointment():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    start_time = datetime(2026, 9, 10, 10, 0)
    end_time = start_time + timedelta(hours=1)

    appointment = service.create_appointment(
        title="Team Meeting",
        description="Weekly meeting",
        start_time=start_time,
        end_time=end_time
    )

    assert appointment.appointment_id == 1
    assert appointment.title == "Team Meeting"
    assert appointment.status == AppointmentStatus.SCHEDULED



import pytest

from exceptions import AppointmentConflictError


def test_create_appointment_when_slot_overlaps():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    start_time = datetime(2026, 9, 10, 10, 0)
    end_time = datetime(2026, 9, 10, 11, 0)

    service.create_appointment(
        title="First Meeting",
        description="First",
        start_time=start_time,
        end_time=end_time
    )

    with pytest.raises(AppointmentConflictError):
        service.create_appointment(
            title="Second Meeting",
            description="Second",
            start_time=datetime(2026, 9, 10, 10, 30),
            end_time=datetime(2026, 9, 10, 11, 30)
        )

def test_create_back_to_back_appointments():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    service.create_appointment(
        title="First Meeting",
        description="First",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    second = service.create_appointment(
        title="Second Meeting",
        description="Second",
        start_time=datetime(2026, 9, 10, 11, 0),
        end_time=datetime(2026, 9, 10, 12, 0)
    )

    assert second.appointment_id == 2    


from exceptions import AppointmentConflictError, InvalidAppointmentTimeError
def test_create_appointment_with_invalid_time():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    with pytest.raises(InvalidAppointmentTimeError):
        service.create_appointment(
            title="Invalid Meeting",
            description="Invalid",
            start_time=datetime(2026, 9, 10, 11, 0),
            end_time=datetime(2026, 9, 10, 10, 0)
        )        


def test_cancel_appointment():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    appointment = service.create_appointment(
        title="Team Meeting",
        description="Weekly meeting",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    service.cancel_appointment(appointment.appointment_id)

    assert appointment.status == AppointmentStatus.CANCELLED 

def test_cancelled_appointment_frees_time_slot():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    appointment = service.create_appointment(
        title="First Meeting",
        description="First",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    service.cancel_appointment(appointment.appointment_id)

    new_appointment = service.create_appointment(
        title="Second Meeting",
        description="Second",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    assert new_appointment.appointment_id == 2    

def test_cancelled_appointment_cannot_be_completed():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    appointment = service.create_appointment(
        title="Team Meeting",
        description="Weekly meeting",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    service.cancel_appointment(appointment.appointment_id)

    with pytest.raises(AppointmentConflictError):
        service.complete_appointment(appointment.appointment_id)

    assert appointment.status == AppointmentStatus.CANCELLED   

def test_completed_appointment_cannot_be_cancelled():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    appointment = service.create_appointment(
        title="Team Meeting",
        description="Weekly meeting",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    service.complete_appointment(appointment.appointment_id)

    with pytest.raises(AppointmentConflictError):
        service.cancel_appointment(appointment.appointment_id)

    assert appointment.status == AppointmentStatus.COMPLETED            

def test_update_appointment():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    appointment = service.create_appointment(
        title="Old Title",
        description="Old Description",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    updated = service.update_appointment(
        appointment_id=appointment.appointment_id,
        title="New Title",
        description="New Description",
        start_time=datetime(2026, 9, 10, 12, 0),
        end_time=datetime(2026, 9, 10, 13, 0)
    )

    assert updated.title == "New Title"
    assert updated.description == "New Description"
    assert updated.start_time == datetime(2026, 9, 10, 12, 0)
    assert updated.end_time == datetime(2026, 9, 10, 13, 0)
    assert updated.status == AppointmentStatus.SCHEDULED 

def test_update_appointment_with_conflicting_time():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    first = service.create_appointment(
        title="First",
        description="First",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    second = service.create_appointment(
        title="Second",
        description="Second",
        start_time=datetime(2026, 9, 10, 12, 0),
        end_time=datetime(2026, 9, 10, 13, 0)
    )

    with pytest.raises(AppointmentConflictError):
        service.update_appointment(
            appointment_id=second.appointment_id,
            title="Second Updated",
            description="Updated",
            start_time=datetime(2026, 9, 10, 10, 30),
            end_time=datetime(2026, 9, 10, 11, 30)
        )       

def test_update_appointment_without_changing_time():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    appointment = service.create_appointment(
        title="Old Title",
        description="Old Description",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    updated = service.update_appointment(
        appointment_id=appointment.appointment_id,
        title="New Title",
        description="New Description",
        start_time=datetime(2026, 9, 10, 10, 0),
        end_time=datetime(2026, 9, 10, 11, 0)
    )

    assert updated.title == "New Title"
    assert updated.description == "New Description"
    assert updated.status == AppointmentStatus.SCHEDULED        


from exceptions import (
    AppointmentConflictError,
    AppointmentNotFoundError,
    InvalidAppointmentTimeError
)

def test_update_nonexistent_appointment():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    with pytest.raises(AppointmentNotFoundError):
        service.update_appointment(
            appointment_id=999,
            title="Test",
            description="Test",
            start_time=datetime(2026, 9, 10, 10, 0),
            end_time=datetime(2026, 9, 10, 11, 0)
        )

def test_cancel_nonexistent_appointment():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    with pytest.raises(AppointmentNotFoundError):
        service.cancel_appointment(999)

def test_complete_nonexistent_appointment():
    repository = InMemoryAppointmentRepository()
    availability_service = AvailabilityService(repository)
    service = AppointmentService(repository, availability_service)

    with pytest.raises(AppointmentNotFoundError):
        service.complete_appointment(999)                