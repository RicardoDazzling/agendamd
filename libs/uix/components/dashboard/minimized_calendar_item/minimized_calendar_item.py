from typing import Optional

from kivy.properties import ListProperty, ObjectProperty

from libs.applibs.utils import ignore_args, ignore_instance
from libs.uix.components.dashboard.base_calendar_item import BaseCalendarItem
from libs.uix.components.dashboard.calendar_item import CalendarItem, CalendarItemNav


class MinimizedCalendarItem(BaseCalendarItem):
    item: Optional[CalendarItem] = ObjectProperty(None)
    nav: Optional[CalendarItemNav] = ObjectProperty(None)
    title: list = ListProperty([])
    day: list = ListProperty([])
    start: list = ListProperty([])
    end: list = ListProperty([])
    description: list = ListProperty([])
    tag: list = ListProperty([])
    closed: list = ListProperty([])
    item_index: int = 0

    def __init__(self, *args, **kwargs):
        super(MinimizedCalendarItem, self).__init__(**kwargs)
        for arg in args:
            if not isinstance(arg, dict):
                raise TypeError("Item isn't from dict type.")
            self.set_properties_by_dict(arg)

        __lbl = self.ids.get('lbl', None)
        if __lbl is not None:
            __lbl.text = self.title[0]

        self.item = CalendarItem(
            item=args[0],
            base_height=self.base_height,
            width=self.width,
            theme_text_color="Hint",
            pos=(
                    self.x,
                    ((24 - self.end[0] / 60) * self.base_height)
                ),
            static_pos=True
        )

        if len(self.title) > 1:
            self.nav = CalendarItemNav()
            self.nav.bind(on_previous_release=self.on_previous_release,
                          on_next_release=self.on_next_release)
            self.item.add_widget(self.nav)

        self.item.bind(on_item_release=self._on_item_release,
                       on_item_press=self._on_item_press,
                       on_leave=self.on_item_leave)
        self.bind(width=self.item.setter('width'))

        self.height = (self.base_height / 4)

    def get_index_by_dict(self, item: dict) -> int:
        for idx in range(len(self.title)):
            if (self.title[idx] == item['title'] and
                    self.day[idx] == item['day'] and
                    self.start[idx] == item['start'] and
                    self.end[idx] == item['end'] and
                    self.description[idx] == item['description'] and
                    self.tag[idx] == item['tag'] and
                    self.closed[idx] == item['closed']):
                return idx
        return -1

    def set_properties_by_dict(self, item: Optional[dict] = None, old: Optional[dict] = None):
        if item is not None:
            title = item.get('title', None)
            day = item.get('day', None)
            start = item.get('start', None)
            end = item.get('end', None)
            description = item.get('description', None)
            tag = item.get('tag', None)
            closed = item.get('closed', None)

            if old is None:
                self.title.append(title)
                self.day.append(day)
                self.start.append(start)
                self.end.append(end)
                self.description.append(description)
                self.tag.append(tag)
                self.closed.append(closed)
            else:
                old_idx = self.get_index_by_dict(old)
                if old_idx == -1:
                    raise IndexError("Old dict doesn't exists.")
                self.title[old_idx] = title
                self.day[old_idx] = day
                self.start[old_idx] = start
                self.end[old_idx] = end
                self.description[old_idx] = description
                self.tag[old_idx] = tag
                self.closed[old_idx] = closed
                if old_idx == self.item_index:
                    self.change_item_index(old_idx)

    def remove_properties_by_dict(self, item: Optional[dict] = None):
        if item is not None:
            idx = self.get_index_by_dict(item)
            if idx == -1:
                raise IndexError("Item doesn't exists.")

            self.title.pop(idx)
            self.day.pop(idx)
            self.start.pop(idx)
            self.end.pop(idx)
            self.description.pop(idx)
            self.tag.pop(idx)
            self.closed.pop(idx)

            if self.item_index == idx:
                self.change_item_index(idx - 1)
            elif self.item_index > idx:
                self.item_index -= 1

    @staticmethod
    def on_pos(self, value: list):
        if self.item is not None and self.end:
            self.item.pos = (
                value[0],
                ((24 - self.end[0] / 60) * self.base_height)
            )

    def on_enter(self, *args):
        if self.hover_visible and self.item.parent is None:
            self.parent.add_widget(self.item)
            self.item.hovering = True
            self.item.hover_visible = True

    @ignore_args
    def on_item_leave(self):
        if not self.item.hover_visible and self.item.parent is not None:
            self.parent.remove_widget(self.item)
            self.hovering = False
            self.hover_visible = False

    @ignore_args
    def on_previous_release(self):
        new_index = self.item_index - 1
        if new_index == -1:
            new_index = len(self.title) - 1
        self.change_item_index(new_index)

    @ignore_args
    def on_next_release(self):
        new_index = self.item_index + 1
        if new_index == len(self.title):
            new_index = 0
        self.change_item_index(new_index)

    def change_item_index(self, index: int):
        self.item_index = index
        self.item.title = self.title[index]
        self.item.day = self.day[index]
        self.item.start = self.start[index]
        self.item.end = self.end[index]
        self.item.description = self.description[index]
        self.item.tag = self.tag[index]
        self.item.closed = self.closed[index]

    @ignore_instance
    def _on_item_release(self):
        self.dispatch("on_item_release")

    @ignore_instance
    def _on_item_press(self):
        self.dispatch("on_item_press")

    @property
    def dict(self) -> dict:
        return self.item.dict
