from kivy.metrics import dp
from kivymd.uix.button import MDButton


class LoginFormButton(MDButton):
    def __init__(self, **kwargs):
        super(LoginFormButton, self).__init__(**kwargs)
        self.style = "filled"
        self.theme_width = "Custom"
        self.height = dp(46)
        self.size_hint_x = .5
        self.pos_hint = {"center_x": .5}