from typing import Optional, Literal

from kivy.properties import ObjectProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextFieldLeadingIcon, MDTextFieldHintText, MDTextFieldMaxLengthText

from globals import USERS, translator as _
from libs.uix.components.login import LoginPasswordTextField

from .flags import *


class PasswordDialogContent(MDBoxLayout):
    focus: bool = BooleanProperty(False)
    focus_next = ObjectProperty(StopIteration)
    focus_previous = ObjectProperty(StopIteration)

    def __init__(self, **kwargs):
        super(PasswordDialogContent, self).__init__(**kwargs)
        self._current = LoginPasswordTextField(
            MDTextFieldLeadingIcon(
                icon="account-key-outline",
            ),
            _.bind_translation(MDTextFieldHintText(), "text", "Current password"),
            MDTextFieldMaxLengthText(
                max_text_length=32,
            ),
        )
        self._new = LoginPasswordTextField(
            MDTextFieldLeadingIcon(
                icon="account-key-outline",
            ),
            _.bind_translation(MDTextFieldHintText(), 'text', "New password"),
            MDTextFieldMaxLengthText(
                max_text_length=32,
            ),
        )
        self._repeat = LoginPasswordTextField(
            MDTextFieldLeadingIcon(
                icon="account-key-outline",
            ),
            _.bind_translation(MDTextFieldHintText(), 'text', "Repeat new password"),
            MDTextFieldMaxLengthText(
                max_text_length=32,
            ),
        )

        self.register_event_type('on_text_validate')
        self.add_widget(self._current)
        self.add_widget(self._new)
        self.add_widget(self._repeat)
        self._current.focus_previous = self.focus_previous
        self._current.focus_next = self._new
        self._new.focus_previous = self._current
        self._new.focus_next = self._repeat
        self._repeat.focus_previous = self._new
        self._repeat.focus_next = self.focus_next
        self._current.bind(on_text_validate=lambda x: self.change_focus("new"))
        self._new.bind(on_text_validate=lambda x: self.change_focus("repeat"))
        self._repeat.bind(on_text_validate=lambda x: self.dispatch("on_text_validate"))

    @staticmethod
    def on_focus(self, value: bool):
        if value:
            self.focus = False
            self._title.focus = True
        else:
            for widget in self.children:
                try:
                    widget.focus = False
                except NameError:
                    pass

    def on_text_validate(self):
        pass

    def get_error_flags(self) -> Optional[PasswordExceptionFlagType]:
        __flags = []
        __current = str(self._current.text).strip()
        __new = str(self._new.text).strip()
        __repeat = str(self._repeat.text).strip()
        __have_empty_fields = False
        if __current == "":
            self._current.error = __have_empty_fields = True
        else:
            self._current.error = False
        if __new == "":
            self._new.error = __have_empty_fields = True
        else:
            self._new.error = False
        if __repeat == "":
            self._repeat.error = __have_empty_fields = True
        else:
            self._repeat.error = False
        if __have_empty_fields:
            return EmptyFieldsException
        if not USERS.compare_password(__current):
            return PasswordException
        __password_out_of_range = False
        if len(__new) > 32:
            self._new.error = __password_out_of_range = True
        else:
            self._new.error = False
        if len(__repeat) > 32:
            self._repeat.error = __password_out_of_range = True
        else:
            self._repeat.error = False
        if __password_out_of_range:
            return TooLongPasswordException
        if __new != __repeat:
            self._repeat.error = True
            return PasswordDoNotMatchException
        return None

    def get_field(self, key: Literal["current", "new", "repeat"]):
        if key == 'current':
            return self._current
        if key == 'new':
            return self._new
        if key == 'repeat':
            return self._repeat
        raise KeyError(f'Invalid key: "{key}"')

    @property
    def new_password(self) -> dict:
        return self._new.text.strip()

    def change_focus(self, wid: Literal["current", "new", "repeat"]):
        self.get_field(wid).focus = True

    def clean(self, text: bool = True, error: bool = True):
        if text:
            self._current.text = ""
            self._new.text = ""
            self._repeat.text = ""

        if error:
            self._current.error = False
            self._new.error = False
            self._repeat.error = False
