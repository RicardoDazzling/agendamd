from kivy.properties import ColorProperty
from kivymd.uix.button import MDButtonText, MDButton

from libs.applibs.utils import ignore_args


class ConfigButtonText(MDButtonText):

    on_press_color = ColorProperty(None)
    on_release_color = ColorProperty(None)

    def __init__(self, **kwargs):
        kwargs['theme_text_color'] = 'Custom'
        super().__init__(**kwargs)
        self.update_colors()
        self.theme_cls.bind(theme_style=self.update_colors)

    @ignore_args
    def update_colors(self):
        self.text_color = self.on_release_color = self.theme_cls.primaryColor
        self.on_press_color = self.theme_cls.onPrimaryColor

    @staticmethod
    def on_parent(self, parent: MDButton):
        parent.bind(on_press=self.switch_color, on_release=self.switch_color)

    @ignore_args
    def switch_color(self):
        if self.on_press_color is None:
            return
        self.text_color = self.on_press_color if self.text_color != self.on_press_color else self.on_release_color

