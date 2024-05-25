from kivy.uix.image import Image
from kivymd.uix.label import MDIcon


class CheckIcon(Image):
    def __init__(self, **kwargs):
        super(CheckIcon, self).__init__(**kwargs)
        label = MDIcon(icon="check", font_style="Display", role="large",
                       text_color=self.theme_cls.primaryColor)
        label.font_size = '1000dp'
        label.texture_update()
        self.texture = label.texture
