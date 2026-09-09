class AppointmentNotFoundError(Exception):
    pass


class AppointmentConflictError(Exception):
    pass

class InvalidAppointmentTimeError(Exception):
    pass