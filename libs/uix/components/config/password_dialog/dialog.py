__all__ = ["PasswordDialog"]

from functools import partial
from typing import Literal

from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, \
    MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.snackbar import (MDSnackbar, MDSnackbarSupportingText, MDSnackbarButtonContainer,
                                 MDSnackbarCloseButton, MDSnackbarText)

from globals import USERS, translator as _
from libs.applibs.utils import ignore_args

from .content import PasswordDialogContent


class PasswordDialog(MDDialog):

    content = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._content = PasswordDialogContent(
            orientation='vertical',
            spacing=dp(20),
            size_hint=(1, None),
            adaptive_height=True
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
        super(PasswordDialog, self).__init__(
            MDDialogIcon(icon='key-variant'),
            MDDialogHeadlineText(text=_('Password Update')),
            MDDialogContentContainer(
                MDDivider(),
                self._content,
                MDDivider(),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                Widget(),
                self._btn_cancel,
                self._btn_accept,
                spacing="8dp",
            ),
            **kwargs
        )

        def accept_focus():
            self._btn_accept.focus = True

        self._content.bind(on_text_validate=lambda x: accept_focus())
        self._btn_cancel.focus_previous = self._content.get_field('repeat')
        self._btn_cancel.focus_next = self._btn_accept
        self._btn_accept.focus_previous = self._btn_cancel
        self._btn_accept.focus_next = self._content.get_field('current')
        self._content.focus_previous = self._btn_accept
        self._content.focus_next = self._btn_cancel
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
        self._success_snackbar = MDSnackbar(
            _.bind_translation(MDSnackbarText(), "text", "Password changed successfully."),
            y=dp(124),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            padding=[0, 0, "8dp", "8dp"]
        )

    @ignore_args
    def _snackbar_dismiss(self, snackbar: Literal['error', 'tag', 'remove'] = 'tag'):
        if snackbar == 'error':
            self._error_snackbar.dismiss()
        else:
            raise KeyError("Unknown snackbar.")

    def clean(self):
        self._content.clean()

    def cancel(self):
        self.dismiss()

    def accept(self):
        __flag = self._content.get_error_flags()
        if __flag is not None:
            self._error_snackbar_text.text = __flag.message
            self._error_snackbar.open()
            return
        __new_password = self._content.new_password
        USERS.update_password(__new_password)
        self.dismiss()
        self._success_snackbar.open()
        return

    def on_dismiss(self, *args) -> None:
        super(TaskDialog, self).on_dismiss(*args)
        self.clean()
