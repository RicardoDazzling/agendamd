from typing import Optional
from datetime import time, date

from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.behaviors import HoverBehavior
from babel.dates import format_time

from globals import CONFIG
from libs.applibs.utils import get_datestamp_from_date
from libs.uix.components.home.static_card import MDStaticCard


class BaseCalendarItem(MDStaticCard, HoverBehavior):
    title = StringProperty(None)
    day = NumericProperty(None)
    start = NumericProperty(None)
    end = NumericProperty(None)
    description = StringProperty(None)
    tag = StringProperty(None)
    closed = BooleanProperty(False)
    base_height = NumericProperty(dp(120))
    static_pos = BooleanProperty(False)

    def __init__(self,
                 base_height: Optional[float] = None,
                 **kwargs):
        kwargs['style'] = "elevated"
        kwargs['padding'] = dp(10)
        kwargs['size_hint'] = (None, None)
        super(BaseCalendarItem, self).__init__(**kwargs)
        self.register_event_type('on_item_release')
        self.register_event_type('on_item_press')
        self.bind(width=self.on_duration, start=self.on_duration, end=self.on_duration)

        if base_height is not None:
            self.base_height = base_height

    def on_duration(self, *args):
        if self.width == 0:
            return
        if isinstance(self.day, list):
            if not self.start or not self.end:
                return
            __day = self.day[0]
            __end = self.start[0] + 15
        else:
            if self.start is None or self.end is None:
                return
            __day = self.day
            __end = self.end
        if not self.static_pos:
            __day_date = __day
            __today = get_datestamp_from_date(date.today()) - 1
            __x = (__day_date - __today) * self.width
            __y = ((24 - __end / 60) * self.base_height)
            self.pos = (__x, __y)

    def format_duration(self) -> str:
        __start_formated = format_time(time(*(divmod(self.start, 60))), format='short', locale=CONFIG.language)
        __end_formated = format_time(time(*(divmod(self.end, 60))), format='short', locale=CONFIG.language)
        return f"{__start_formated} - {__end_formated}"

    def set_properties_by_dict(self, item: Optional[dict] = None, old: Optional[dict] = None):
        if item is not None:

            title = item.get('title', None)
            if title is not None:
                self.title = title

            day = item.get('day', None)
            if day is not None:
                self.day = day

            start = item.get('start', None)
            if start is not None:
                self.start = start

            end = item.get('end', None)
            if end is not None:
                self.end = end

            description = item.get('description', None)
            if description is not None:
                self.description = description

            tag = item.get('tag', None)
            if tag is not None:
                self.tag = tag

            closed = item.get('closed', None)
            if closed is not None:
                self.closed = closed

    def on_item_release(self, *args):
        pass

    def on_item_press(self, *args):
        pass

    @property
    def dict(self) -> dict:
        return {
            "title": self.title,
            "day": self.day,
            "start": self.start,
            "end": self.end,
            "description": self.description,
            "tag": self.tag,
            "closed": self.closed
        }
