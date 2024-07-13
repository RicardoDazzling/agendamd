from typing import Optional, Literal, Union
from datetime import date, time

from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon, MDTextFieldHintText, MDTextFieldMaxLengthText

from globals import TAGS, translator as _
from libs.applibs.utils import get_datestamp_from_date, get_date_from_datestamp
from libs.uix.components.home import CalendarItem
from libs.uix.components.textfields import DateTimeTextField, ComboTextField

from .task_dialog_error_flags import *


class TaskDialogContent(MDBoxLayout):
    focus: bool = BooleanProperty(False)
    focus_next = ObjectProperty(StopIteration)
    focus_previous = ObjectProperty(StopIteration)

    def __init__(self, item: Optional[CalendarItem] = None, **kwargs):
        super(TaskDialogContent, self).__init__(**kwargs)
        self._title = MDTextField(
            MDTextFieldLeadingIcon(
                icon="alphabetical-variant",
            ),
            MDTextFieldHintText(
                text=_("Title"),
            ),
            MDTextFieldMaxLengthText(
                max_text_length=int(CONFIG.task_max_title_size),
            ),
            mode="outlined"
        )
        self._day = DateTimeTextField(
            MDTextFieldLeadingIcon(
                icon="calendar-outline",
            ),
            MDTextFieldHintText(
                text=_("Date"),
            ),
            mode="outlined",
            datetime_mode="date",
            locale=CONFIG.language
        )
        self._start = DateTimeTextField(
            MDTextFieldLeadingIcon(
                icon="calendar-outline",
            ),
            MDTextFieldHintText(
                text=_("Start"),
            ),
            mode="outlined",
            datetime_mode="time",
            locale=CONFIG.language
        )
        self._end = DateTimeTextField(
            MDTextFieldLeadingIcon(
                icon="calendar-outline",
            ),
            MDTextFieldHintText(
                text=_("End"),
            ),
            mode="outlined",
            datetime_mode="time",
            locale=CONFIG.language
        )
        self._description = MDTextField(
            MDTextFieldHintText(
                text=_("Description"),
            ),
            MDTextFieldMaxLengthText(
                max_text_length=int(CONFIG.task_max_description_size),
            ),
            mode="outlined",
            multiline=True,
            max_height=dp(200)
        )
        self._tag = ComboTextField(
            MDTextFieldLeadingIcon(
                icon="tag-hidden",
            ),
            MDTextFieldHintText(
                text=_("Tag"),
            ),
            MDTextFieldMaxLengthText(
                max_text_length=int(CONFIG.task_max_tag_size),
            ),
            data=list(TAGS),
            accept_unknown=True,
            mode="outlined"
        )
        if item is not None:
            self.complete_by_item(item)

        self.register_event_type('on_text_validate')
        self.add_widget(self._title)
        self.add_widget(self._day)
        self.add_widget(self._start)
        self.add_widget(self._end)
        self.add_widget(self._description)
        self.add_widget(self._tag)
        self._title.focus_previous = self.focus_previous
        self._title.focus_next = self._day
        self._day.focus_previous = self._title
        self._day.focus_next = self._start
        self._start.focus_previous = self._day
        self._start.focus_next = self._end
        self._end.focus_previous = self._start
        self._end.focus_next = self._description
        self._description.focus_previous = self._end
        self._description.focus_next = self._tag
        self._tag.focus_previous = self._description
        self._tag.focus_next = self.focus_next
        self._title.bind(on_text_validate=lambda x: self.change_focus("day"))
        self._day.bind(on_text_validate=lambda x: self.change_focus("start"))
        self._start.bind(on_text_validate=lambda x: self.change_focus("end"))
        self._end.bind(on_text_validate=lambda x: self.change_focus("description"))
        self._description.bind(on_text_validate=lambda x: self.change_focus("tag"))
        self._tag.bind(on_text_validate=lambda x: self.dispatch("on_text_validate"))

        def _set_outline(instance: Union[DateTimeTextField, ComboTextField], value):
            __icon = instance.leading_icon
            hyphen = '-hidden' if 'tag' in __icon else '-outline'
            __icon = __icon.replace(hyphen, '')
            instance.leading_icon = __icon + ('' if value else hyphen)

        self._day.bind(focus=_set_outline)
        self._start.bind(focus=_set_outline)
        self._end.bind(focus=_set_outline)
        self._tag.bind(focus=_set_outline)

    @staticmethod
    def on_focus(self, value: bool):
        if value:
            self._title.focus = True
        else:
            for widget in self.children:
                try:
                    widget.focus = False
                except NameError:
                    pass

    def on_text_validate(self):
        pass

    def complete_by_item(self, item: CalendarItem):
        self.clean(text=False, datetime=False)

        self._title.text = "" if item.title is None else item.title

        if item.day is not None:
            self._day.date = get_date_from_datestamp(item.day)
        else:
            self._day.text = ""
            self._day.date = None

        if item.start is not None:
            hour, minute = divmod(item.start, 60)
            self._start.time = time(hour=hour, minute=minute)
        else:
            self._start.text = ""
            self._start.time = None

        if item.end is not None:
            hour, minute = divmod(item.start, 60)
            self._end.time = time(hour=hour, minute=minute)
        else:
            self._end.text = ""
            self._end.time = None

        self._description.text = "" if item.description is None else item.description

        self._tag.text = "" if item.tag is None else item.tag

    def get_error_flags(self) -> list:
        __flags = []
        if 3 > len(str(self._title.text)) > int(CONFIG.task_max_title_size):
            self._title.error = True
            __flags.append(TitleOutOfRange())
        else:
            self._title.error = False
        if self._day.date is None:
            self._day.error = True
            __flags.append(DayIsRequired())
        else:
            self._day.error = False
        if self._start.time is None:
            self._start.error = True
            __flags.append(StartIsRequired())
        else:
            self._start.error = False
        if self._end.time is not None:
            if self.start + 15 < self.end:
                self._end.error = False
            else:
                self._end.error = True
                __flags.append(EndIsInvalid())
        else:
            self._end.error = True
            __flags.append(EndIsRequired())
        if len(self._description.text) > int(CONFIG.task_max_description_size):
            __flags.append(DescriptionOutOfRange())
        if self._tag.selected is None:
            if 3 > len(self._tag.text) > int(CONFIG.task_max_tag_size):
                self._tag.error = True
                __flags.append(TagOutOfRange())
            else:
                self._tag.error = True
                __flags.append(TagNotExists())
        else:
            self._tag.error = False
        return __flags

    def get_field(self, key: Literal["title", "day", "start", "end", "description", "tag"]):
        if key == 'title':
            return self._title
        if key == 'day':
            return self._day
        if key == 'start':
            return self._start
        if key == 'end':
            return self._end
        if key == 'description':
            return self._description
        if key == 'tag':
            return self._tag
        raise KeyError('Invalid key.')

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "day": self.day,
            "start": self.start,
            "end": self.end,
            "description": self.description,
            "tag": self.tag
        }

    def change_focus(self, wid: Literal["title", "day", "start", "end", "description", "tag"]):
        self.get_field(wid).focus = True

    def clean(self, text: bool = True, error: bool = True, datetime: bool = True):
        if text:
            self._title.text = ""
            self._day.text = ""
            self._start.text = ""
            self._end.text = ""
            self._description.text = ""
            self._tag.text = ""
            self._tag.dropdown.dismiss()

        if error:
            self._title.error = False
            self._day.error = False
            self._start.error = False
            self._end.error = False
            self._description.error = False
            self._tag.error = False

        if datetime:
            self._day.date = None
            self._start.time = None
            self._end.time = None

    @property
    def title(self) -> str:
        return self._title.text

    @property
    def day(self) -> Optional[int]:
        __date = self._day.date
        if not isinstance(__date, date):
            return None
        return get_datestamp_from_date(__date)

    @property
    def start(self) -> Optional[int]:
        __time = self._start.time
        if not isinstance(__time, time):
            return None
        return __time.hour * 60 + __time.minute

    @property
    def end(self) -> Optional[int]:
        __time = self._end.time
        if not isinstance(__time, time):
            return None
        return __time.hour * 60 + __time.minute

    @property
    def description(self) -> str:
        return self._description.text

    @property
    def tag(self) -> str:
        __selected = self._tag.selected
        if __selected is None:
            return self._tag.text
        return __selected
