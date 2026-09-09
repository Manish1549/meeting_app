from fastapi import APIRouter
from models.appointment_status import AppointmentStatus
from dependencies import appointment_service
from schemas.appointment import CreateAppointmentRequest,UpdateAppointmentRequest, AppointmentResponse
from datetime import date
router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

@router.post("", response_model=AppointmentResponse)
def create_appointment(request: CreateAppointmentRequest):
    return appointment_service.create_appointment(
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time
    )


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    appointment_date: date | None = None,
    status: AppointmentStatus | None = None
):
    return appointment_service.list_appointments(
        appointment_date=appointment_date,
        status=status
    )

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    request: UpdateAppointmentRequest
):
    return appointment_service.update_appointment(
        appointment_id=appointment_id,
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time
    )

@router.patch("/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    appointment_service.cancel_appointment(appointment_id)
    return {"message": "Appointment cancelled successfully."}

@router.patch("/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    appointment_service.complete_appointment(appointment_id)
    return {"message": "Appointment completed successfully."}