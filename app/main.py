from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.appointment_router import router as appointment_router
from exceptions import AppointmentConflictError, AppointmentNotFoundError, InvalidAppointmentTimeError
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


@app.exception_handler(AppointmentConflictError)
async def appointment_conflict_handler(
    request: Request,
    exc: AppointmentConflictError
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )
@app.exception_handler(AppointmentNotFoundError)
async def appointment_not_found_handler(
    request: Request,
    exc: AppointmentNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(InvalidAppointmentTimeError)
async def invalid_appointment_time_handler(
    request: Request,
    exc: InvalidAppointmentTimeError
):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

app.include_router(appointment_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)