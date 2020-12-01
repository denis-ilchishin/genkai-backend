class NotificationRelatedError(Exception):
    pass


class NotificationInvalidType(NotificationRelatedError):
    pass


class NotificationRelatedInvalid(NotificationRelatedError):
    pass


class NotificationRelatedNotSaved(NotificationRelatedError):
    pass
