from kivy.app import App
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel


class CheckIcon(Image):
    def __init__(self, **kwargs):
        super(CheckIcon, self).__init__(**kwargs)
        self._app = App.get_running_app()
        label = MDLabel(text="✔", font_style="Display", role="large", theme_text_color="Custom",
                        text_color=self._app.theme_cls.onPrimaryColor)
        label.font_size = '1000dp'
        label.texture_update()
        self.texture = label.texture
