from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from calendar import Calendar, SUNDAY, month_name, day_name
from datetime import datetime, timedelta


class Dashboard(MDScreen):

    cell_height = dp(50)

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self._calendar = Calendar(SUNDAY)
        self._datetime = datetime.now()
        self._update_header()
        self._update_dashboard_calendar()

    def _update_header(self):
        __header: MDRelativeLayout = self.ids.calendar_header
        __cell_width = __header.width // 6
        __datetime = datetime.now()
        for i in range(6):
            __header.add_widget(
                MDBoxLayout(
                    MDLabel(text=day_name[__datetime.weekday()], theme_text_color="Hint"),
                    MDLabel(text=__datetime.day),
                    orientation="vertical",
                    size_hint=(None, None),
                    width=__cell_width,
                    height=self.cell_height,
                    pos=(i * __cell_width, 0)
                )
            )
            __datetime += timedelta(days=1)

    def _update_dashboard_calendar(self):
        self.ids.lbl_year.text = str(self._datetime.year)
        self.ids.lbl_month.text = month_name[self._datetime.month]
        __calendar: MDRelativeLayout = self.ids.calendar
        __cell_width = __calendar.width // 6
        self._create_basics(__calendar, __cell_width)
        __tasks = self.app.DB.dashboard_tasks
        for i in range(5):
            # Todo: add a CalendarItem to each task
            pass

    def _create_basics(self, calendar: MDRelativeLayout, cell_width: int) -> None:
        for i in range(24):
            calendar.add_widget(MDBoxLayout(
                MDLabel(
                    text="{:02d}:00".format(i),
                    theme_text_color="Hint"
                ),
                size_hint=(None, None),
                height=self.cell_height,
                width=cell_width,
                pos=(0, i * cell_width)
            ))
        for i in range(1, 6):
            calendar.add_widget(MDDivider(
                orientation="vertical",
                size_hint_y=1,
                x=self.cell_width * i
            ))

