from functools import partial
from typing import Optional

from kivy.clock import Clock
from kivymd.uix.label import MDLabel

from libs.uix.components.home.base_calendar_item import BaseCalendarItem

from .calendar_item_nav import CalendarItemNav


class CalendarItem(BaseCalendarItem):

    def __init__(self, *args, **kwargs):
        super(CalendarItem, self).__init__(*args, **kwargs)

        self.bind(on_release=partial(self.dispatch, "on_item_release"),
                  on_press=partial(self.dispatch, "on_item_press"))

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, CalendarItemNav):
            for children in self.ids.item_header.children:
                if isinstance(children, CalendarItemNav):
                    self.ids.item_header.remove_widget(children)
            self.ids.item_header.add_widget(widget)
            return
        super(CalendarItem, self).add_widget(widget, *args, **kwargs)

    def remove_widget(self, widget):
        if isinstance(widget, CalendarItemNav):
            self.ids.item_header.remove_widget(widget)
            return
        super(CalendarItem, self).remove_widget(widget)

    @staticmethod
    def on_description(self, value: Optional[str]):
        if value is None or value == "":
            return

        label = self.ids.get('lbl_description', None)
        if self.height >= self.base_height and label is None:
            self.ids['lbl_description'] = MDLabel(id='lbl_description',
                                                  font_style="Body",
                                                  role="small",
                                                  halign="justify",
                                                  text=self.description)
            self.bind(description=self.ids['lbl_description'].setter('text'))
            Clock.schedule_once(lambda x: self.ids.box_description.add_widget(self.ids.lbl_description))

    def on_theme_text_color(self, instance, value):
        if isinstance(value, str):
            self.ids.check_icon.theme_icon_color = value
            self.ids.lbl_title.theme_text_color = value
            self.ids.lbl_description.theme_text_color = value
            self.ids.lbl_duration.theme_text_color = value
            self.ids.lbl_tag.theme_text_color = value

    def on_duration(self, *args):
        if self.start is None or self.end is None:
            return
        super().on_duration(*args)

        self.height = self.base_height * ((self.end - self.start) / 60)
        self.ids.lbl_duration.text = self.format_duration()

    def on_closed(self, *args):
        with self.ids.check_icon.canvas:
            self.ids.check_icon.opacity = .5 if self.closed else 0
