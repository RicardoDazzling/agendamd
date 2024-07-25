from kivy.metrics import dp
from kivy.properties import BooleanProperty, OptionProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton


class CalendarItemNavButton(MDIconButton):
    direction = OptionProperty('left', options=['left', 'right'])

    def __init__(self, **kwargs):
        super(CalendarItemNavButton, self).__init__(**kwargs)
        self.theme_font_size = 'Custom'
        self.font_size = dp(12)
        self.icon = self.get_icon()
        self.update_metrics()
        self.pos_hint = {'top': 1}

    def get_icon(self, outlined: bool = True) -> str:
        if self.direction == 'left':
            if outlined:
                return 'arrow-left-drop-circle-outline'
            else:
                return 'arrow-left-drop-circle'
        else:
            if outlined:
                return 'arrow-right-drop-circle-outline'
            else:
                return 'arrow-right-drop-circle'

    def update_metrics(self, *args):
        self.size_hint = (None, None)
        self.size = (dp(20), dp(20))

    on_size = update_metrics
    on_size_hint = update_metrics

    def on_press(self):
        super(CalendarItemNavButton, self).on_press()
        self.icon = self.get_icon(outlined=False)

    def on_release(self):
        super(CalendarItemNavButton, self).on_release()
        self.icon = self.get_icon(outlined=True)


class CalendarItemNav(MDBoxLayout):

    previous_disabled: bool = BooleanProperty(False)
    next_disabled: bool = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        __adaptive_width = kwargs.get('adaptive_width', None)
        if __adaptive_width is None:
            kwargs['adaptive_width'] = True
        super(CalendarItemNav, self).__init__(*args, **kwargs)
        self.spacing = dp(5)
        __theme_font_size = 'Custom'
        __font_size = '12dp'
        self._previous_btn = CalendarItemNavButton(
            direction='left',
            disabled=self.previous_disabled
        )
        self._next_btn = CalendarItemNavButton(
            direction='right',
            disabled=self.next_disabled
        )
        self.register_event_type('on_previous_press')
        self.register_event_type('on_previous_release')
        self.register_event_type('on_next_press')
        self.register_event_type('on_next_release')
        self.bind(previous_disabled=self._previous_btn.setter("disabled"),
                  next_disabled=self._next_btn.setter("disabled"))
        self._previous_btn.bind(
            on_press=lambda i: self.dispatch("on_previous_press"),
            on_release=lambda i: self.dispatch("on_previous_release"),
            disabled=self.setter("previous_disabled")
        )
        self._next_btn.bind(
            on_press=lambda i: self.dispatch("on_next_press"),
            on_release=lambda i: self.dispatch("on_next_release"),
            disabled=self.setter("next_disabled")
        )
        self.add_widget(self._previous_btn)
        self.add_widget(self._next_btn)

    def on_previous_press(self, *args):
        pass

    def on_previous_release(self, *args):
        pass

    def on_next_press(self, *args):
        pass

    def on_next_release(self, *args):
        pass
