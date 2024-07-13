from globals import (CONFIG, translator as _)


class TaskDialogErrorFlags(ValueError):
    _message: str = 'A task error flag has been set.'

    @property
    def message(self):
        return self._message


class TitleOutOfRange(TaskDialogErrorFlags):
    _message: str = _('Title need to stay between 3 and {0} characters')

    @property
    def message(self):
        return format(self._message, CONFIG.task_max_title_size)


class DayIsRequired(TaskDialogErrorFlags):
    _message: str = _('Date is required')


class StartIsRequired(TaskDialogErrorFlags):
    _message: str = _("Start Time is required")


class EndIsRequired(TaskDialogErrorFlags):
    _message: str = _("End Time is required")


class EndIsInvalid(TaskDialogErrorFlags):
    _message: str = _("The task duration require 15 minutes or more")


class DescriptionOutOfRange(TaskDialogErrorFlags):
    _message: str = _("The description can't exceed {0} characters")

    @property
    def message(self):
        return format(self._message, CONFIG.task_max_description_size)


class TagNotExists(TaskDialogErrorFlags):
    _message: str = _("Unknown Tag")


class TagOutOfRange(TaskDialogErrorFlags):
    _message: str = _("The Tag name can't exceed {0} characters")

    @property
    def message(self):
        return format(self._message, CONFIG.task_max_tag_size)
