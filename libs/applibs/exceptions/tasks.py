

class TaskException(Exception):
    pass


class TaskTimeAlreadyInUseException(TaskException):
    pass


class TaskAlreadyExistsException(TaskException):
    pass


class TaskNotExistsException(TaskException):
    pass


class MonthFolderNotFoundException(TaskException):
    pass
