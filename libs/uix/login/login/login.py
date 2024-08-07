from libs.applibs.db.users import USERS

from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText

from libs.applibs.exceptions.login import PasswordException, EMailException, UserNotExistException, \
    TooLongPasswordException
from libs.uix.components.login.snackbar import LoginSnackbar
from globals import translator as _


class LoginScreen(MDScreen):

    snackbar = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snackbar = LoginSnackbar(supporting_text="Usuário não encontrado!",
                                      action_text="Registrar",
                                      action=self.goto_register)
        self.bind(on_pre_leave=lambda _self: self.clean(True))
        
    def on_pre_leave(self, *args):
        super().on_pre_leave(*args)
        __cb_keep = self.ids.get('cb_keep', None)
        if __cb_keep is not None:
            __cb_keep.active = USERS.keep_logged

    def login(self,
              tf_email: MDTextField,
              help_email: MDTextFieldHelperText,
              tf_password: MDTextField,
              help_password: MDTextFieldHelperText):
        __email = tf_email.text
        __password = tf_password.text
        self.clean()
        if __email.strip(" ") == "":
            tf_email.error = True
            tf_email.required = True
            help_email.text = _("Email is required!")
            return
        if __password.strip(" ") == "":
            tf_password.error = True
            tf_password.required = True
            help_password.text = _("Password is required!")
            return
        try:
            USERS.login(email=__email, password=__password, keep_logged=self.ids.cb_keep.active)
            USERS.decrypt_database()
            self.goto_main()
        except UserNotExistException:
            self.snackbar.open()
        except EMailException:
            tf_email.error = True
            help_email.text = _("Invalid Email.")
        except TooLongPasswordException:
            tf_password.error = True
            help_password.text = _("Too long Password, max 32 characters.")
        except PasswordException:
            tf_password.error = True
            help_password.text = _("Invalid Password.")

    def clean(self, text: bool = False):
        if text:
            self.ids.tf_email.text = self.ids.tf_password.text = ""
        self.ids.tf_email.error = self.ids.tf_password.error = False
        self.ids.help_email.text = self.ids.help_password.text = ""

    def goto_register(self):
        register_screen = self.manager.get_screen("register")

        register_screen.ids.tf_email.text = self.ids.tf_email.text
        register_screen.ids.tf_password.text = self.ids.tf_password.text

        self.manager.switch_to("register")

    def goto_main(self):
        self.manager.switch_to("home")
