from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldHelperText

from libs.applibs.exceptions.login import EMailException, NameException


class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
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
        __name_is_not_alpha = not __name.isalpha()
        __name_out_of_range = not (3 <= len(__name) <= 80)
        if __name_is_empty:
            tf_name.error = True
            help_name.text = "Nome é obrigatório!"
        elif __name_is_not_alpha:
            tf_name.error = True
            help_name.text = "Nome só pode conter caracteres alfabéticos."
        elif __name_out_of_range:
            tf_name.error = True
            help_name.text = "Nome precisa ter mais que três e menos que oitenta caracteres."
        if __email_is_empty:
            tf_email.error = True
            help_email.text = "Email é obrigatório!"
        if __password_is_empty:
            tf_password.error = True
            help_password.text = "Senha é obrigatória!"
        if __name_is_empty or __name_is_not_alpha or __name_out_of_range or __email_is_empty or __password_is_empty:
            return
        try:
            self.app.DB.register(name=__name, email=__email, password=__password)
            self.goto_main()
        except EMailException:
            tf_email.error = True
            help_email.text = "Email inválido."
        except NameException:
            tf_name.error = True
            help_name.text = "Nome não é alfabético."

    def clean(self, text: bool = False):
        if text:
            self.ids.tf_email.text = self.ids.tf_password.text = self.ids.tf_name.text = ""
        self.ids.tf_email.error = self.ids.tf_password.error = self.ids.tf_name.error = False
        self.ids.help_email.text = self.ids.help_password.text = self.ids.help_name.text = ""

    def goto_login(self, *args):
        login_screen = self.manager.get_screen("login")

        login_screen.ids.tf_email.text = self.ids.tf_email.text
        login_screen.ids.tf_password.text = self.ids.tf_password.text

        self.manager.switch_to("login", direction='right')

    def goto_main(self):
        self.manager.switch_to("home")
