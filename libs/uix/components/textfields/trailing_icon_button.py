__all__ = ['MDTextFieldTrailingIconButton']

from typing import Optional

from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivymd.uix.textfield import MDTextFieldTrailingIcon, MDTextField


class MDTextFieldTrailingIconButton(MDTextFieldTrailingIcon, EventDispatcher):
    text_field = ObjectProperty(None)

    def __init__(self, text_field: Optional[MDTextField] = None, **kwargs):
        if text_field is not None:
            self.text_field = text_field
        super(MDTextFieldTrailingIconButton, self).__init__(**kwargs)

        self.register_event_type('on_press')
        Window.bind(on_mouse_down=self.on_mouse_down)

    def on_press(self, *args):
        pass

    def on_mouse_down(self, *args):  # (0) window: WindowSDL, (1) x: int, (2) y: int, (3) button: str, (4...) *modifiers
        button = args[3]
        if self.text_field is not None and button == 'left':
            txt = self.text_field
            x_start = (txt.width + txt.x) - (self.texture_size[1]) - dp(14)
            y_start = (txt.center_y - self.texture_size[1] / 2)
            x_end = x_start + self.texture_size[0]
            y_end = y_start + self.texture_size[1]
            if x_start <= Window.mouse_pos[0] <= x_end and y_start <= Window.mouse_pos[1] <= y_end:
                self.dispatch('on_press')

