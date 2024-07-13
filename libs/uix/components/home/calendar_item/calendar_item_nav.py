from functools import partial

from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText


class CalendarItemNav(MDBoxLayout):

    previous_disabled: bool = BooleanProperty(False)
    next_disabled: bool = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(CalendarItemNav, self).__init__(*args, **kwargs)
        self.spacing = dp(5)
        self._previous_btn = MDButton(
            MDButtonText(
                text="⮜"
            ),
            disabled=self.previous_disabled,
            style="text",
            adaptive_size=True
        )
        self._next_btn = MDButton(
            MDButtonText(
                text="⮞"
            ),
            disabled=self.next_disabled,
            style="text",
            adaptive_size=True
        )
        self.register_event_type('on_previous_press')
        self.register_event_type('on_previous_release')
        self.register_event_type('on_next_press')
        self.register_event_type('on_next_release')
        self.bind(previous_disabled=self._previous_btn.setter("disabled"),
                  next_disabled=self._next_btn.setter("disabled"))
        self._previous_btn.bind(
            on_press=partial(self.dispatch, event_type="on_previous_press"),
            on_release=partial(self.dispatch, event_type="on_previous_release"),
            disabled=self.setter("previous_disabled")
        )
        self._next_btn.bind(
            on_press=partial(self.dispatch, event_type="on_next_press"),
            on_release=partial(self.dispatch, event_type="on_next_release"),
            disabled=self.setter("next_disabled")
        )

    def on_previous_press(self, *args):
        pass

    def on_previous_release(self, *args):
        pass

    def on_next_press(self, *args):
        pass

    def on_next_release(self, *args):
        pass
