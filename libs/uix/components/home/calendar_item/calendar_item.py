from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.card import MDCard
from datetime import datetime
from babel.dates import format_datetime
from ctypes import windll
from locale import windows_locale


class CalendarItem(MDCard):

    title = StringProperty()
    start = NumericProperty()
    end = NumericProperty()
    description = StringProperty()
    tag = StringProperty()
    closed = BooleanProperty(False)
    base_height = NumericProperty(dp(50))

    def __init__(self, **kwargs):
        super(CalendarItem, self).__init__(**kwargs)
        self.bind(start=self.on_duration, end=self.on_duration, closed=self.on_closed)
        self._language = windows_locale[windll.kernel32.GetUserDefaultUILanguage()]

    def on_duration(self, *args):
        __start_dt = datetime.fromtimestamp(self.start)
        __end_dt = datetime.fromtimestamp(self.end)

        __delta = __end_dt - __start_dt
        self.height = self.base_height * (__delta.total_seconds() / 60)

        __duration = f"{
                format_datetime(__start_dt, locale=self._language)
            } - {
                format_datetime(__end_dt, locale=self._language)
            }"

        self.ids.lbl_duration.text = __duration

    def on_closed(self, *args):
        with self.ids.check_icon.canvas:
            self.ids.check_icon.opacity = .5 if self.closed else 0
