from kivy.metrics import dp
from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import *
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText

from libs.applibs.exceptions.login import PasswordException, EMailException, UserNotExistException


class LoginScreen(MDScreen):

    snackbar = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.snackbar = MDSnackbar(
            MDSnackbarText(
                text="Aviso!"
            ),
            MDSnackbarSupportingText(
                text="Usuário não encontrado!"
            ),
            MDSnackbarButtonContainer(
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(
                        text="Registrar"
                    ),
                    on_release=self.goto_register
                ),
                MDSnackbarCloseButton(
                    icon="close",
                    on_release=self.snackbar_dismiss,
                ),
                pos_hint={"center_y": 0.5}
            ),
            orientation="horizontal",
            y=dp(24),
            size_hint=(None, None),
            width=dp(500),
            pos_hint={"center_x": 0.5},
        )
        self.bind(on_pre_leave=lambda _self: self.clean(True))

    def snackbar_dismiss(self, *args):
        self.snackbar.dismiss(*args)

    def login(self,
              tf_email: MDTextField,
              help_email: MDTextFieldHelperText,
              tf_password: MDTextField,
              help_password: MDTextFieldHelperText):
        __email = tf_email.text
        __password = tf_password.text
        self.clean()
        if __email == "":
            tf_email.error = True
            tf_email.required = True
            help_email.text = "Email é obrigatório!"
            return
        if __password == "":
            tf_password.error = True
            tf_password.required = True
            help_password.text = "Senha é obrigatória!"
            return
        try:
            self.app.DB.login(email=__email, password=__password)
            self.goto_main()
        except UserNotExistException:
            self.snackbar.open()
        except EMailException:
            tf_email.error = True
            help_email.text = "Email inválido."
        except PasswordException:
            tf_password.error = True
            help_password.text = "Senha inválida."

    def clean(self, text: bool = False):
        if text:
            self.ids.tf_email.text = self.ids.tf_password.text = ""
        self.ids.tf_email.error = self.ids.tf_password.error = False
        self.ids.help_email.text = self.ids.help_password.text = ""

    def goto_register(self, *args):
        register_screen = self.manager.get_screen("register")

        register_screen.ids.tf_email.text = self.ids.tf_email.text
        register_screen.ids.tf_password.text = self.ids.tf_password.text

        self.manager.switch_to("register")

    def goto_main(self):
        self.manager.switch_to("home")
