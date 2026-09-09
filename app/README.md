````markdown
# Appointment Board

A simple appointment management system built with **FastAPI, Python, Pydantic, and vanilla HTML/CSS/JavaScript**.

The application allows a small team to create, view, update, complete, and cancel appointments while preventing conflicting time slots.
---

## Features

- Create appointments
- View all appointments
- Filter appointments by date
- Filter appointments by status
- Filter by date and status together
- Update scheduled appointments
- Cancel appointments
- Complete appointments
- Prevent overlapping appointments
- Allow back-to-back appointments
- Cancelled appointments remain visible
- Cancelled appointment slots become available again
- Prevent invalid state transitions
- Validate appointment time ranges
- Proper HTTP error responses
- Unit tests for core business logic
- Simple browser-based frontend

---

# Tech Stack

## Backend

- Python 3.12+
- FastAPI
- Pydantic
- Uvicorn
- pytest
- uv for dependency and environment management

## Frontend

- HTML
- CSS
- Vanilla JavaScript
- Fetch API

No frontend framework is required.

---

# Project Structure

```text
appointment_board/
└── app/
    ├── pyproject.toml
    ├── .venv/
    │
    ├── main.py
    ├── dependencies.py
    ├── exceptions.py
    │
    ├── api/
    │   ├── __init__.py
    │   └── appointment_router.py
    │
    ├── models/
    │   ├── __init__.py
    │   ├── appointment.py
    │   └── appointment_status.py
    │
    ├── repositories/
    │   ├── __init__.py
    │   ├── appointment_repository.py
    │   └── in_memory_appointment_repository.py
    │
    ├── services/
    │   ├── __init__.py
    │   ├── appointment_service.py
    │   └── availability_service.py
    │
    ├── schemas/
    │   ├── __init__.py
    │   └── appointment.py
    │
    ├── tests/
    │   └── test_appointment_service.py
    │
    └── frontend/
        └── index.html
````

---

# Architecture

The project follows a layered architecture.

```text
                    HTTP Request
                         │
                         ▼
                ┌─────────────────┐
                │ FastAPI Router  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Appointment     │
                │ Service         │
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌─────────────────┐   ┌─────────────────┐
     │ Availability    │   │ Appointment     │
     │ Service         │   │ Repository      │
     └────────┬────────┘   └────────┬────────┘
              │                     │
              └──────────┬──────────┘
                         ▼
              ┌─────────────────────┐
              │ In-Memory Repository│
              └─────────────────────┘
```

The main responsibilities are separated between layers.

---

# Layer Responsibilities

## 1. API / Router

Location:

```text
api/appointment_router.py
```

Responsible for:

* HTTP endpoints
* Request parameters
* Request body parsing
* Calling the application service
* Returning responses

The router should not contain business rules.

For example:

```python
@router.post("", response_model=AppointmentResponse)
def create_appointment(request: CreateAppointmentRequest):
    return appointment_service.create_appointment(
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time
    )
```

The router simply translates the HTTP request into a service call.

---

# 2. Service Layer

Location:

```text
services/
```

The service layer contains the application's business logic.

### AppointmentService

Responsible for:

* Creating appointments
* Updating appointments
* Cancelling appointments
* Completing appointments
* Listing appointments
* Enforcing appointment state transitions
* Coordinating availability checks

### AvailabilityService

Responsible for:

* Validating start/end times
* Checking whether a requested time slot is available
* Detecting overlapping appointments

Separating availability logic from appointment management keeps each service focused on one responsibility.

---

# 3. Repository Layer

Location:

```text
repositories/
```

The repository abstracts data storage.

The application does not directly manipulate the underlying storage mechanism.

The service depends on:

```python
AppointmentRepository
```

rather than:

```python
InMemoryAppointmentRepository
```

This is important because the storage implementation can later be replaced.

For example:

```text
Current:

AppointmentService
        ↓
AppointmentRepository
        ↓
InMemoryAppointmentRepository


Possible future:

AppointmentService
        ↓
AppointmentRepository
        ↓
PostgresAppointmentRepository
```

The service layer does not need to change when the storage mechanism changes.

---

# 4. Domain Model

Location:

```text
models/
```

The main domain object is:

```text
Appointment
```

An appointment contains:

* `appointment_id`
* `title`
* `description`
* `start_time`
* `end_time`
* `created_at`
* `updated_at`
* `status`

The status is represented using an enum:

```python
class AppointmentStatus(Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
```

---

# 5. Pydantic Schemas

Location:

```text
schemas/appointment.py
```

The API uses separate schemas for incoming and outgoing data.

### CreateAppointmentRequest

Used when creating an appointment.

```text
title
description
start_time
end_time
```

### UpdateAppointmentRequest

Used when updating an appointment.

```text
title
description
start_time
end_time
```

### AppointmentResponse

Used for API responses.

```text
appointment_id
title
description
start_time
end_time
created_at
updated_at
status
```

Keeping request and response models separate allows the API contract to evolve independently from the internal domain model.

---

# Appointment Lifecycle

An appointment follows these state transitions:

```text
                 ┌───────────────┐
                 │   SCHEDULED   │
                 └───────┬───────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       ┌──────────────┐      ┌──────────────┐
       │  COMPLETED   │      │  CANCELLED   │
       └──────────────┘      └──────────────┘
```

Valid transitions:

```text
SCHEDULED → COMPLETED
SCHEDULED → CANCELLED
```

Invalid transitions:

```text
COMPLETED → CANCELLED
COMPLETED → SCHEDULED
CANCELLED → COMPLETED
CANCELLED → SCHEDULED
```

Completed and cancelled appointments are considered terminal states.

---

# Appointment Update Rules

Only scheduled appointments can be updated.

```text
SCHEDULED
    │
    │ update
    ▼
SCHEDULED
```

Completed appointments cannot be updated.

Cancelled appointments cannot be updated.

This prevents the system from modifying historical appointment states.

---

# Overlap Detection

The system prevents two active appointments from occupying the same time slot.

Two appointments overlap when:

```python
existing.start_time < requested.end_time
and
existing.end_time > requested.start_time
```

For example:

```text
Appointment A:
10:00 ───────── 11:00

Appointment B:
10:30 ───────── 11:30

Result:
CONFLICT
```

---

## Back-to-back appointments

Back-to-back appointments are allowed.

```text
Appointment A:
10:00 ───────── 11:00

Appointment B:
                    11:00 ───────── 12:00
```

These do not overlap.

This is achieved using strict `<` and `>` comparisons.

---

# Cancelled Appointments

Cancelling an appointment does **not delete it**.

Instead:

```text
SCHEDULED
    ↓
CANCELLED
```

The appointment remains stored and visible.

However, cancelled appointments are ignored during availability checks.

Therefore:

```text
10:00 ───────── 11:00
CANCELLED
```

allows another appointment to use:

```text
10:00 ───────── 11:00
```

This preserves appointment history while making the slot available again.

---

# Update Availability

When updating an appointment, the appointment being updated must be excluded from the overlap search.

Otherwise, the appointment would conflict with itself.

For example:

```text
Appointment #1
10:00 ───────── 11:00
```

If we update its title while keeping the same time, the availability check must ignore appointment `#1`.

This is handled through:

```python
exclude_appointment_id=appointment_id
```

---

# Dependency Injection

The application uses dependency injection to connect its layers.

The dependencies are created in:

```text
dependencies.py
```

The current setup is:

```text
InMemoryAppointmentRepository
            ↓
AvailabilityService
            ↓
AppointmentService
```

Conceptually:

```python
repository = InMemoryAppointmentRepository()

availability_service = AvailabilityService(repository)

appointment_service = AppointmentService(
    repository,
    availability_service
)
```

This makes the business logic independent of the concrete repository implementation.

It also makes unit testing easier because tests can construct fresh dependencies.

---

# SOLID Principles Used

## Single Responsibility Principle

Different classes have different responsibilities.

```text
Appointment
    → domain data

AppointmentService
    → appointment business operations

AvailabilityService
    → availability rules

Repository
    → persistence

Router
    → HTTP/API handling
```

This avoids putting all application logic into one large class.

---

## Open/Closed Principle

The service depends on the repository abstraction.

New repository implementations can be added without changing the service.

For example:

```text
InMemoryAppointmentRepository
PostgresAppointmentRepository
MongoAppointmentRepository
```

can all implement:

```text
AppointmentRepository
```

---

## Dependency Inversion Principle

`AppointmentService` depends on:

```python
AppointmentRepository
```

rather than directly depending on:

```python
InMemoryAppointmentRepository
```

The high-level business logic therefore does not depend on a specific storage implementation.

---

# Error Handling

The application defines custom exceptions.

```python
AppointmentNotFoundError
AppointmentConflictError
InvalidAppointmentTimeError
```

These are mapped to HTTP responses by FastAPI.

### 400 Bad Request

Used for invalid appointment times.

Example:

```text
start_time >= end_time
```

Response:

```json
{
    "detail": "Start time must be before end time."
}
```

---

### 404 Not Found

Used when an appointment ID does not exist.

Example:

```text
PUT /appointments/999
```

Response:

```json
{
    "detail": "Appointment with ID 999 does not exist."
}
```

---

### 409 Conflict

Used for business conflicts.

Examples:

* Overlapping appointment
* Updating a completed appointment
* Cancelling a completed appointment
* Completing a cancelled appointment

Example:

```json
{
    "detail": "The requested time slot is not available."
}
```

---

# API Endpoints

Base URL:

```text
http://127.0.0.1:8000
```

---

## Create Appointment

```http
POST /appointments
```

Request:

```json
{
    "title": "Team Meeting",
    "description": "Weekly project discussion",
    "start_time": "2026-09-10T10:00:00",
    "end_time": "2026-09-10T11:00:00"
}
```

Response:

```json
{
    "appointment_id": 1,
    "title": "Team Meeting",
    "description": "Weekly project discussion",
    "start_time": "2026-09-10T10:00:00",
    "end_time": "2026-09-10T11:00:00",
    "created_at": "...",
    "updated_at": "...",
    "status": "SCHEDULED"
}
```

---

# List Appointments

```http
GET /appointments
```

Returns all appointments.

---

## Filter by Date

```http
GET /appointments?appointment_date=2026-09-10
```

---

## Filter by Status

```http
GET /appointments?status=SCHEDULED
```

Supported statuses:

```text
SCHEDULED
COMPLETED
CANCELLED
```

---

## Filter by Date and Status

```http
GET /appointments?appointment_date=2026-09-10&status=SCHEDULED
```

---

# Update Appointment

```http
PUT /appointments/{appointment_id}
```

Example:

```http
PUT /appointments/1
```

Request:

```json
{
    "title": "Updated Meeting",
    "description": "Updated description",
    "start_time": "2026-09-10T12:00:00",
    "end_time": "2026-09-10T13:00:00"
}
```

Only scheduled appointments can be updated.

---

# Cancel Appointment

```http
PATCH /appointments/{appointment_id}/cancel
```

Example:

```http
PATCH /appointments/1/cancel
```

Response:

```json
{
    "message": "Appointment cancelled successfully."
}
```

The appointment is not deleted.

---

# Complete Appointment

```http
PATCH /appointments/{appointment_id}/complete
```

Example:

```http
PATCH /appointments/1/complete
```

Response:

```json
{
    "message": "Appointment completed successfully."
}
```

---

# Running the Backend

## 1. Go to the application directory

```powershell
cd D:\appointment_board\app
```

---

## 2. Install dependencies

The project uses `uv`.

If dependencies are not installed:

```powershell
uv sync
```

---

## 3. Start FastAPI

```powershell
uv run fastapi dev main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Swagger Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You can test all API endpoints directly from Swagger.

Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# Running the Frontend

The frontend is currently a single HTML file:

```text
frontend/index.html
```

It contains:

* HTML
* CSS
* JavaScript

The JavaScript communicates with the FastAPI backend using the Fetch API.

The frontend supports:

* Loading appointments
* Filtering
* Creating
* Editing
* Completing
* Cancelling
* Displaying API errors

---

# Frontend → Backend Communication

The frontend uses:

```javascript
fetch()
```

to communicate with:

```text
http://127.0.0.1:8000
```

Example:

```javascript
fetch("http://127.0.0.1:8000/appointments")
```

Creating an appointment:

```javascript
fetch("http://127.0.0.1:8000/appointments", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(appointment)
})
```

---

# CORS

Because the frontend and backend may run on different origins during development, FastAPI is configured with CORS middleware.

For local development, the project allows cross-origin requests.

For a production deployment, `allow_origins` should be restricted to the actual frontend domain.

---

# Testing

The project uses `pytest`.

Install pytest as a development dependency:

```powershell
uv add --dev pytest
```

Run tests:

```powershell
$env:PYTHONPATH="."
uv run pytest
```

---

# Current Test Coverage

The service layer currently contains tests for:

### Appointment creation

* Valid appointment creation
* Overlapping appointment rejection
* Back-to-back appointments
* Invalid time range

### Cancellation

* Cancelling scheduled appointments
* Cancelled appointments freeing their time slot
* Preventing completion of cancelled appointments

### Completion

* Completing scheduled appointments
* Preventing cancellation of completed appointments

### Updates

* Updating scheduled appointments
* Preventing conflicting updates
* Updating without changing the existing time slot
* Preventing updates of nonexistent appointments

### Error handling

* Updating nonexistent appointment
* Cancelling nonexistent appointment
* Completing nonexistent appointment

Current test suite:

```text
14 passed
```

---

# Unit Testing Approach

Tests create their own dependencies:

```python
repository = InMemoryAppointmentRepository()

availability_service = AvailabilityService(repository)

service = AppointmentService(
    repository,
    availability_service
)
```

This keeps tests isolated.

Each test starts with a fresh repository, so one test does not depend on data created by another test.

---

# Why In-Memory Storage?

The assignment focuses primarily on appointment management and application design.

An in-memory repository keeps the implementation simple:

```python
self.appointments: dict[int, Appointment]
```

This allows the business logic and API to be demonstrated without introducing database configuration.

The repository abstraction also means a database can be added later without changing the core business logic significantly.

---

# Future Improvements

The current implementation intentionally keeps the system simple for the assignment/demo.

Possible improvements include:

## Database

Replace:

```text
InMemoryAppointmentRepository
```

with:

```text
PostgresAppointmentRepository
```

and persist appointments in PostgreSQL.

---

## Authentication

Add users and authentication so appointments can be associated with team members.

Possible technologies:

* JWT
* OAuth2
* Session-based authentication

---

## Better Frontend

The current frontend uses vanilla JavaScript.

A production application could use:

* React
* Vue
* Angular

---

## Pagination

For a large number of appointments:

```text
GET /appointments?page=1&page_size=20
```

could be added.

---

## Better Date Filtering

The current date filtering is based on the appointment's start date.

A future version could support:

* Date ranges
* Weekly view
* Monthly view
* Calendar view

---

## Persistent IDs

The current in-memory repository generates IDs using:

```python
len(self.appointments) + 1
```

This is sufficient because appointments are not deleted in the current implementation.

With a database, IDs would typically be generated by the database or use UUIDs.

---

# Design Decisions

## Why cancel instead of delete?

A cancelled appointment is still useful historical information.

Therefore:

```text
Cancel ≠ Delete
```

Cancellation changes the appointment's status while preserving the record.

---

## Why separate AppointmentService and AvailabilityService?

Appointment management and availability checking are different responsibilities.

Separating them follows SRP and makes the availability rules easier to modify independently.

---

## Why use an abstract repository?

The service should not care whether appointments are stored:

* In memory
* PostgreSQL
* MySQL
* MongoDB
* Another storage system

It only needs the repository contract.

---

## Why separate Pydantic schemas from domain models?

Pydantic models represent the API contract.

The `Appointment` model represents the domain object.

This separation prevents the API layer from becoming tightly coupled to the internal domain representation.

---

# Request Flow Example

Creating an appointment:

```text
Browser
   │
   │ POST /appointments
   ▼
FastAPI Router
   │
   │ CreateAppointmentRequest
   ▼
AppointmentService
   │
   ▼
AvailabilityService
   │
   ▼
AppointmentRepository
   │
   ▼
InMemoryAppointmentRepository
   │
   ▼
Appointment created
   │
   ▼
AppointmentResponse
   │
   ▼
JSON Response
```

---

# Example User Flow

### 1. Create appointment

```text
Team Meeting
10:00 - 11:00
SCHEDULED
```

### 2. Try to create another appointment

```text
10:30 - 11:30
```

The system rejects it:

```text
409 Conflict
```

### 3. Cancel the first appointment

```text
SCHEDULED → CANCELLED
```

### 4. Create another appointment

```text
10:00 - 11:00
```

This now succeeds because cancelled appointments do not block availability.

### 5. Complete an appointment

```text
SCHEDULED → COMPLETED
```

Completed appointments remain visible but cannot be modified or cancelled.

---

# Project Goals

The primary goals of this project are:

1. Demonstrate clean separation of responsibilities.
2. Implement appointment lifecycle management.
3. Prevent conflicting appointments.
4. Provide a simple REST API.
5. Demonstrate dependency injection.
6. Demonstrate repository abstraction.
7. Demonstrate SOLID principles.
8. Provide a usable browser interface.
9. Validate important business rules through unit tests.

---

# Status

The core appointment management functionality is complete.

```text
Backend       ✅
REST API      ✅
Validation    ✅
Business Rules ✅
Error Handling ✅
Unit Tests    ✅
Frontend      ✅
```

The project is currently designed as a simple demonstration application and can be extended with persistent storage, authentication, and a more advanced frontend when required.

```

### One recommendation

Since this is for a **demo/interview assignment**, this README is detailed enough to show that you understand the architecture—not just that you made endpoints.

I'd also add a small **Screenshots** section at the top once your frontend is finalized. That makes the GitHub repository look considerably more polished.
```
