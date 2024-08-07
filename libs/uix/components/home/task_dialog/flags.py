from globals import (USERS, translator as _)


class TaskDialogErrorFlags(ValueError):
    _message: str = 'A task error flag has been set.'

    @property
    def message(self):
        return _(self._message)


class TitleOutOfRange(TaskDialogErrorFlags):
    _message: str = 'Title need to stay between 3 and {0} characters'

    @property
    def message(self):
        return format(super().message, USERS.task_max_title_size)


class DayIsRequired(TaskDialogErrorFlags):
    _message: str = 'Date is required'


class StartIsRequired(TaskDialogErrorFlags):
    _message: str = "Start Time is required"


class EndIsRequired(TaskDialogErrorFlags):
    _message: str = "End Time is required"


class EndIsInvalid(TaskDialogErrorFlags):
    _message: str = "The task duration require 15 minutes or more"


class DescriptionOutOfRange(TaskDialogErrorFlags):
    _message: str = "The description can't exceed {0} characters"

    @property
    def message(self):
        return format(super().message, USERS.task_max_description_size)


class TagNotExists(TaskDialogErrorFlags):
    _message: str = "Unknown Tag"


class TagOutOfRange(TaskDialogErrorFlags):
    _message: str = "The Tag name can't exceed {0} characters"

    @property
    def message(self):
        return format(super().message, USERS.task_max_tag_size)
