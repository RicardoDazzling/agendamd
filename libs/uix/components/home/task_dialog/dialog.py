from functools import partial
from typing import Optional, Literal

from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, \
    MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.snackbar import (MDSnackbar, MDSnackbarSupportingText, MDSnackbarButtonContainer,
                                 MDSnackbarActionButton, MDSnackbarActionButtonText, MDSnackbarCloseButton,
                                 MDSnackbarText)

from globals import TAGS, TASKS, translator as _
from libs.applibs.utils import ignore_args, ignore_instance
from libs.uix.components.dashboard import CalendarItem
from libs.uix.components.textfields import ComboTextField

from .content import TaskDialogContent, TagNotExists


class TaskDialog(MDDialog):
    content = ObjectProperty(None)
    item = ObjectProperty(None, allownone=True)

    def __init__(self, item: Optional[CalendarItem] = None, **kwargs):
        self._dialog_content = TaskDialogContent(
            item=item,
            orientation='vertical',
            spacing=dp(20),
            size_hint=(1, None),
            adaptive_height=True
        )
        self._btn_remove = MDButton(
            _.bind_translation(MDButtonText(), "text", "Remove"),
            style="text",
            theme_text_color='Error',
            on_release=self.remove,
        )
        self._btn_cancel = MDButton(
            _.bind_translation(MDButtonText(), "text", "Cancel"),
            style="text",
            on_release=lambda i: self.cancel(),
        )
        self._btn_accept = MDButton(
            _.bind_translation(MDButtonText(), "text", "Accept"),
            style="text",
            on_release=lambda i: self.accept(),
        )
        super(TaskDialog, self).__init__(
            MDDialogIcon(icon='check'),
            _.bind_translation(MDDialogHeadlineText(), "text", 'Create or Update a Task'),
            _.bind_translation(MDDialogSupportingText(), "text",
                               'In this window you can create or update a task. '
                               'Next, you can see the task fields, please complete and edit then,'
                               ' and click in Accept. If your editing a task that exists and'
                               ' click in Remove, the task will be removed.'),
            MDDialogContentContainer(
                MDDivider(),
                self._dialog_content,
                MDDivider(),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                self._btn_remove,
                Widget(),
                self._btn_cancel,
                self._btn_accept,
                spacing="8dp",
            ),
            **kwargs
        )

        def accept_focus():
            self._btn_accept.focus = True

        self._dialog_content.bind(
            on_text_validate=lambda x: accept_focus(),
            on_new_tag=self.on_new_tag
        )
        self._btn_cancel.focus_previous = self._btn_remove
        self._btn_cancel.focus_next = self._btn_accept
        self._btn_accept.focus_previous = self._btn_cancel
        self._btn_accept.focus_next = self._dialog_content.get_field('title')
        self._dialog_content.focus_previous = self._btn_accept
        self._dialog_content.focus_next = self._btn_remove
        self._btn_remove.focus_previous = self._dialog_content.get_field('tag')
        self._btn_remove.focus_next = self._btn_cancel
        self.item = item
        self._error_snackbar_text = MDSnackbarSupportingText(
            text="Error!!!!",
            padding=[0, 0, 0, dp(56)],
        )
        self._error_snackbar = MDSnackbar(
            _.bind_translation(MDSnackbarText(), "text", "Errors occurred in the task creation:"),
            self._error_snackbar_text,
            MDSnackbarButtonContainer(
                Widget(),
                MDSnackbarCloseButton(
                    icon="close",
                    on_release=partial(self._snackbar_dismiss, snackbar="error")
                ),
            ),
            y=dp(124),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            padding=[0, 0, "8dp", "8dp"],
            auto_dismiss=False
        )
        self._new_tag_snackbar = MDSnackbar(
            _.bind_translation(MDSnackbarSupportingText(), "text", "This tag doesn't exists, want to create this?"),
            MDSnackbarButtonContainer(
                MDSnackbarActionButton(
                    _.bind_translation(MDSnackbarActionButtonText(), "text", "Create"),
                    on_release=self._create_tag
                ),
                MDSnackbarCloseButton(
                    icon="close",
                    on_release=partial(self._snackbar_dismiss, snackbar="tag")
                ),
                pos_hint={"center_y": 0.5}
            ),
            y=dp(24),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            auto_dismiss=False
        )
        __action_remove_button = _.bind_translation(MDSnackbarActionButtonText(
            theme_text_color="Custom",
            text_color=self.theme_cls.errorColor
        ), "text", "Continue")
        self.theme_cls.bind(errorColor=__action_remove_button.setter('text_color'))
        self._rusure_snackbar = MDSnackbar(
            _.bind_translation(MDSnackbarText(), "text", "Are you sure?"),
            _.bind_translation(MDSnackbarSupportingText(), "text", "After remove, this task can't be recovered."),
            MDSnackbarButtonContainer(
                MDSnackbarActionButton(
                    __action_remove_button,
                    on_release=self.remove
                ),
                MDSnackbarCloseButton(
                    icon="close",
                    on_release=partial(self._snackbar_dismiss, snackbar="remove")
                ),
                pos_hint={"center_y": 0.5}
            ),
            y=dp(24),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            auto_dismiss=False
        )

    @ignore_args
    def _create_tag(self):
        self._new_tag_snackbar.dismiss()
        __tag_field: ComboTextField = self._dialog_content.get_field('tag')
        TAGS.add(__tag_field.text)
        __data = __tag_field.data
        if isinstance(__data, list):
            __data = __data.copy()
            __data.append(__tag_field.text)
            __tag_field.data = __data
        else:
            __tag_field.data = [__tag_field.text]

    @ignore_args
    def _snackbar_dismiss(self, snackbar: Literal['error', 'tag', 'remove'] = 'tag'):
        if snackbar == 'error':
            self._error_snackbar.dismiss()
        elif snackbar == 'tag':
            self._new_tag_snackbar.dismiss()
        elif snackbar == 'remove':
            self._rusure_snackbar.dismiss()
        else:
            raise KeyError("Unknown snackbar.")

    def clean(self):
        self._dialog_content.clean()
        self.item = None

    def remove(self, instance=None):
        if self.item is None:
            self.cancel()
        if not isinstance(instance, MDSnackbarActionButton):
            self._rusure_snackbar.open()
            return
        __task_dict = self.item.dict
        __task_dict["tag"] = TAGS.get(__task_dict["tag"])
        TASKS.remove(__task_dict)
        self.dismiss()

    def cancel(self):
        self.dismiss()

    def accept(self):
        __flags = self._dialog_content.get_error_flags()
        if __flags:
            __messages = []
            for flag in __flags:
                if isinstance(flag, TagNotExists):
                    self._new_tag_snackbar.open()
                    return
                __messages.append(flag.message)
            self._error_snackbar_text.text = ";\n".join(__messages) + "."
            self._error_snackbar.open()
            return
        __new_task_dict = self._dialog_content.to_dict()
        __new_task_dict["tag"] = TAGS.get(__new_task_dict["tag"])
        __new_task_dict["closed"] = False
        if self.item is not None:
            __old_task_dict = self.item.dict
            __old_task_dict["tag"] = TAGS.get(__old_task_dict["tag"])
            TASKS[__old_task_dict] = __new_task_dict
        else:
            TASKS.add(__new_task_dict)
        self.dismiss()

    def on_dismiss(self, *args) -> None:
        super(TaskDialog, self).on_dismiss(*args)
        self.clean()

    @ignore_args
    def on_new_tag(self):
        self._new_tag_snackbar.open()

    @ignore_instance
    def on_item(self, value):
        if isinstance(value, CalendarItem):
            self._dialog_content.complete_by_item(value)
        elif value is None:
            self._dialog_content.clean()
        else:
            raise TypeError(f"The item need to be a CalendarItem. Give: '{type(value)}'.")
