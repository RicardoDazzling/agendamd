from libs.applibs.db.users import USERS

from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText

from libs.applibs.exceptions.login import EMailException, NameException, UserAlreadyExistsException, \
    TooLongPasswordException
from libs.uix.components.login.login_components import LoginSnackbar
from globals import translator as _


class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snackbar = LoginSnackbar(supporting_text="Usuário já existe!",
                                      action_text="Login",
                                      action=self.goto_login)
        self.bind(on_pre_leave=lambda _self: self.clean(True))

    def register(self,
                 tf_name: MDTextField,
                 help_name: MDTextFieldHelperText,
                 tf_email: MDTextField,
                 help_email: MDTextFieldHelperText,
                 tf_password: MDTextField,
                 help_password: MDTextFieldHelperText):
        __name = tf_name.text
        __email = tf_email.text
        __password = tf_password.text
        self.clean()
        __name_is_empty = __name == ""
        __email_is_empty = __email == ""
        __password_is_empty = __password == ""
        __name_out_of_range = not (3 <= len(__name) <= 80)
        if __name_is_empty:
            tf_name.error = True
            help_name.text = _("Name is required!")
        elif __name_out_of_range:
            tf_name.error = True
            help_name.text = _("Name need to stay between three and eighty characters.")
        if __email_is_empty:
            tf_email.error = True
            help_email.text = _("Email is required!")
        if __password_is_empty:
            tf_password.error = True
            help_password.text = _("Password is required!")
        if __name_is_empty or __name_out_of_range or __email_is_empty or __password_is_empty:
            return
        try:
            USERS.register(__name, __email, __password, keep_logged=self.ids.cb_keep.active)
            self.goto_main()
        except EMailException:
            tf_email.error = True
            help_email.text = _("Invalid Email.")
        except NameException:
            tf_name.error = True
            help_name.text = _("Name not alphabetic.")
        except TooLongPasswordException:
            tf_password.error = True
            help_password.text = _("Too long Password, max 32 characters.")
        except UserAlreadyExistsException:
            self.snackbar.open()

    def clean(self, text: bool = False):
        if text:
            self.ids.tf_email.text = self.ids.tf_password.text = self.ids.tf_name.text = ""
        self.ids.tf_email.error = self.ids.tf_password.error = self.ids.tf_name.error = False
        self.ids.help_email.text = self.ids.help_password.text = self.ids.help_name.text = ""

    def goto_login(self):
        login_screen = self.manager.get_screen("login")

        login_screen.ids.tf_email.text = self.ids.tf_email.text
        login_screen.ids.tf_password.text = self.ids.tf_password.text

        self.manager.switch_to("login", direction='right')

    def goto_main(self):
        self.manager.switch_to("home")
