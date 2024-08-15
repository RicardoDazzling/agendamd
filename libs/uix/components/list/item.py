from datetime import time

from babel.dates import format_date, format_time
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.card import MDCardSwipe, MDCardSwipeLayerBox, MDCardSwipeFrontBox
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTertiaryText
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.selectioncontrol import MDCheckbox

from globals import translator as _
from libs.applibs.utils import get_date_from_datestamp, ignore_args, ignore_instance


class ListItem(MDCardSwipe):
    title = StringProperty(None)
    day = NumericProperty(None)
    start = NumericProperty(None)
    end = NumericProperty(None)
    description = StringProperty(None)
    tag = StringProperty(None)
    closed = BooleanProperty(False)

    def __init__(self, task: dict, **kwargs):
        if 'adaptive_height' not in kwargs:
            kwargs['adaptive_height'] = True
        super(ListItem, self).__init__(**kwargs)
        self.register_event_type('on_list_release')
        self.register_event_type('on_checked_changed')

        self.task = task

        self._headline_label = MDListItemHeadlineText(text=self._set_headline_text())
        self._supporting_label = MDListItemSupportingText(text=self._set_supporting_text())
        self._tertiary_label = MDListItemTertiaryText(text=self._set_tertiary_text())
        self._list_item = MDListItem(
            self._headline_label,
            self._supporting_label,
            self._tertiary_label,
            ripple_effect=False
        )
        self._checkbox = MDCheckbox(active=self.closed, adaptive_size=True, pos_hint={'center_x': .5, 'center_y': .5})
        __layout = MDRelativeLayout(self._checkbox, size_hint=(None, 1), width=self.max_opened_x)
        self.bind(max_opened_x=__layout.setter('width'))
        self.add_widget(MDCardSwipeLayerBox(__layout))
        self.add_widget(MDCardSwipeFrontBox(self._list_item))

        self.bind(title=self._set_headline_text,

                  day=self._set_supporting_text,
                  start=self._set_supporting_text,
                  end=self._set_supporting_text,

                  description=self._set_tertiary_text,
                  tag=self._set_tertiary_text,

                  closed=lambda i, v: getattr(i, '_checkbox', object()).__setattr__('active', v))
        _.bind(self._set_supporting_text)
        self._checkbox.bind(active=self._on_checked_changed)
        self._list_item.bind(on_release=self._on_list_release)

    def on_list_release(self):
        pass

    def on_checked_changed(self, value: bool):
        pass

    @ignore_args
    def _set_headline_text(self):
        if self.title is None:
            return ''
        if hasattr(self, '_headline_label'):
            self._headline_label.text = self.title
        return self.title

    @ignore_args
    def _set_supporting_text(self):
        if None in (self.day, self.start, self.end):
            return ''
        __supporting_text = self._format_datetime(day=self.day,
                                                  start=self.start,
                                                  end=self.end)
        if hasattr(self, '_supporting_label'):
            self._supporting_label.text = __supporting_text
        return __supporting_text

    @ignore_args
    def _set_tertiary_text(self):
        if None in (self.description, self.tag):
            return ''
        __tertiary_text = self._format_tertiary(description=self.description,
                                                tag=self.tag)
        if hasattr(self, '_tertiary_label'):
            self._tertiary_label.text = __tertiary_text
        return __tertiary_text

    @staticmethod
    def _format_datetime(day: int, start: int, end: int) -> str:
        __date = format_date(get_date_from_datestamp(day), format="short", locale=_.language)
        __start = format_time(time(*(divmod(start, 60))), format="short", locale=_.language)
        __end = format_time(time(*(divmod(end, 60))), format="short", locale=_.language)
        return f"{__date}: {__start} - {__end}"

    @staticmethod
    def _format_tertiary(description: str, tag: str) -> str:
        return ((f"{description} - " if description else '') + (f"({tag})" if tag else '')).rstrip(' - ')

    @ignore_args
    def _on_list_release(self):
        if self.open_progress != .0:
            return
        self.dispatch('on_list_release')

    @ignore_instance
    def _on_checked_changed(self, value: bool):
        if value == self.closed:
            return
        self.dispatch('on_checked_changed', value)
        self.closed = value

    @property
    def task(self) -> dict:
        return {
            'title': self.title if self.title else None,
            'day': self.day,
            'start': self.start,
            'end': self.end,
            'description': self.description if self.description else None,
            'tag': self.tag if self.tag else None,
            'closed': self.closed
        }

    @task.setter
    def task(self, value: dict):
        self.title = value.get('title', '')
        self.day = value.get('day', 0)
        self.start = value.get('start', 0)
        self.end = value.get('end', self.start + 15)
        self.description = value.get('description', '')
        self.tag = value.get('tag', '')
        self.closed = value.get('closed', False)
