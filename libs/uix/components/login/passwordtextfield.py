from libs.applibs.utils import ignore_args
from libs.uix.components.textfields import MDTextFieldTrailingIconButton

from .textfield import LoginTextField


class LoginPasswordTextField(LoginTextField):

    def __init__(self, *args, **kwargs):
        super(LoginPasswordTextField, self).__init__(
            MDTextFieldTrailingIconButton(icon="eye-off", text_field=self),
            *args,
            **kwargs
        )
        self.password = True
        self._trailing_icon.bind(on_press=self.show_password)

    @ignore_args
    def show_password(self):
        if self._trailing_icon.icon == "eye-off":
            self.password = False
            self._trailing_icon.icon = "eye"
        elif self._trailing_icon.icon == "eye":
            self.password = True
            self._trailing_icon.icon = "eye-off"
